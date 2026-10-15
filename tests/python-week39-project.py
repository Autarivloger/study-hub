"""Real API integration tests. Only fictional accounts/owned temp files."""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'docs'/'python-week39'))
import jwt
from fastapi.testclient import TestClient
from werkzeug.security import check_password_hash
from learning_api import AUDIENCE, ISSUER, create_app
from learning_api.database import connect, initialise, transaction
from lesson_support import PRACTICE_PASSWORD, login, practice, register


def main():
    with practice() as (app, client, asha):
        ben = login(client, 'ben')
        assert client.get('/health').json() == {'status': 'ok'}
        assert client.get('/v1/me').status_code == 401
        assert client.get('/v1/me').headers['www-authenticate'] == 'Bearer'
        assert client.get('/v1/me', headers=asha).json() == {'id': 1, 'username': 'asha'}
        assert client.get('/v1/notes', headers=asha).json()['total'] == 3
        assert client.get('/v1/notes', headers=ben).json()['total'] == 0
        initial = client.get('/v1/notes/1', headers=asha).json()
        for method, payload in [('get', None), ('put', {'title': 'Other', 'body': 'Body', 'completed': False}),
                                ('patch', {'completed': True}), ('delete', None)]:
            kwargs = {'headers': ben}
            if payload is not None:
                kwargs['json'] = payload
            response = getattr(client, method)('/v1/notes/1', **kwargs)
            assert response.status_code == 404
            assert response.json() == {'detail': 'Note not found'}
        assert client.get('/v1/notes/1', headers=asha).json() == initial

        payload = {'title': '  Created  ', 'body': '  Body  ', 'completed': False}
        created = client.post('/v1/notes', headers=asha, json=payload)
        assert created.status_code == 201
        url = created.headers['location']
        note = created.json()
        assert url == f'/v1/notes/{note["id"]}'
        assert note['title'] == 'Created' and note['body'] == 'Body'
        assert 'owner_id' not in note
        assert client.get(url, headers=asha).json() == note
        assert client.patch(url, headers=asha, json={'completed': True}).json()['completed'] is True
        assert client.patch(url, headers=asha, json={'completed': False}).json()['completed'] is False
        assert client.patch(url, headers=asha, json={'title': 'Changed'}).json()['body'] == 'Body'
        assert client.put(url, headers=asha, json={'title': 'Incomplete'}).status_code == 422
        replacement = {'title': 'Complete', 'body': 'New body', 'completed': False}
        assert client.put(url, headers=asha, json=replacement).json()['created_at'] == note['created_at']
        for patch in ({}, {'completed': None}, {'title': None}, {'body': '   '},
                      {'owner_id': 2}, {'completed': 'false'}, {'completed': 0}):
            assert client.patch(url, headers=asha, json=patch).status_code == 422
        before = client.get('/v1/notes', headers=asha).json()['total']
        for invalid in ({'title': '   ', 'body': 'B'}, {'title': 'A', 'body': ' '},
                        {'title': 'A'*101, 'body': 'B'}, {'title': 'A', 'body': 'B'*2001},
                        {'title': 'A', 'body': 'B', 'owner_id': 2},
                        {'title': 'A', 'body': 'B', 'completed': 'false'}):
            assert client.post('/v1/notes', headers=asha, json=invalid).status_code == 422
        assert client.get('/v1/notes', headers=asha).json()['total'] == before
        for bad in ('limit=0', 'limit=51', 'offset=-1', 'offset=10001', 'q='+'x'*81):
            assert client.get('/v1/notes?'+bad, headers=asha).status_code == 422
        for bad in ('0', '-1', 'nope'):
            assert client.get('/v1/notes/'+bad, headers=asha).status_code == 422
        assert client.get('/v1/notes/999', headers=asha).status_code == 404
        page = client.get('/v1/notes?limit=1&offset=1', headers=asha).json()
        assert page['total'] == before and len(page['items']) == 1
        assert page['items'][0]['title'] == 'Validation'
        assert client.get('/v1/notes?offset=100', headers=asha).json()['items'] == []
        for q, expected in [('http', 1), ('%', 1), ('_', 0), ("' OR 1=1 --", 0)]:
            assert client.get('/v1/notes', headers=asha, params={'q': q}).json()['total'] == expected
        assert register(client, 'asha').status_code == 409
        assert client.get('/v1/me', headers=login(client)).status_code == 200
        unknown = client.post('/v1/token', data={'username': 'missing', 'password': PRACTICE_PASSWORD})
        wrong = client.post('/v1/token', data={'username': 'asha', 'password': 'fictional-wrong-password'})
        assert unknown.status_code == wrong.status_code == 401 and unknown.json() == wrong.json()
        assert client.post('/v1/token', json={'username': 'asha', 'password': PRACTICE_PASSWORD}).status_code == 422
        marker = 'x7Q!z'
        rejected = client.post('/v1/users', json={'username': 'canary', 'password': marker})
        assert rejected.status_code == 422 and marker not in rejected.text
        assert all(set(e) == {'loc', 'msg', 'type'} for e in rejected.json()['detail'])

        db = connect(app.state.database)
        try:
            stored = db.execute('SELECT password_hash FROM users WHERE username=?', ('asha',)).fetchone()[0]
            assert stored != PRACTICE_PASSWORD and check_password_hash(stored, PRACTICE_PASSWORD)
            assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
            count = db.execute('SELECT count(*) FROM notes').fetchone()[0]
            try:
                with transaction(db):
                    db.execute('UPDATE notes SET title=? WHERE id=?', ('Should roll back', 1))
                    db.execute('INSERT INTO users(username,password_hash) VALUES(?,?)', ('asha', 'fictional'))
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError('Expected uniqueness constraint failure')
            assert not db.in_transaction
            assert db.execute('SELECT title FROM notes WHERE id=1').fetchone()[0] == 'HTTP'
            assert db.execute('SELECT count(*) FROM notes').fetchone()[0] == count
        finally:
            db.close()

        encoded = asha['Authorization'].split(' ', 1)[1]
        claims = jwt.decode(encoded, app.state.key, algorithms=['HS256'], issuer=ISSUER, audience=AUDIENCE)
        assert claims['exp']-claims['iat'] == 900
        assert not {'password', 'password_hash', 'body'} & set(claims)
        cases = [({**claims, 'exp': int(time.time())-60}, 'HS256'),
                 ({**claims, 'aud': 'wrong'}, 'HS256'), ({**claims, 'iss': 'wrong'}, 'HS256'),
                 ({**claims, 'jti': 'not-issued'}, 'HS256'), ({**claims, 'sub': '999'}, 'HS256'),
                 ({**claims, 'kind': 'refresh'}, 'HS256'), ({**claims, 'jti': []}, 'HS256'),
                 ({**claims, 'exp': float(claims['exp'])}, 'HS256'), (claims, 'HS384')]
        for changed, algorithm in cases:
            # All keys and signed claim variations belong only to this fictional test app.
            candidate = jwt.encode(changed, app.state.key if algorithm == 'HS256' else b'x'*48, algorithm=algorithm)
            assert client.get('/v1/me', headers={'Authorization': 'Bearer '+candidate}).status_code == 401
        missing = dict(claims); missing.pop('exp')
        candidate = jwt.encode(missing, app.state.key, algorithm='HS256')
        assert client.get('/v1/me', headers={'Authorization': 'Bearer '+candidate}).status_code == 401
        parts = encoded.split('.'); parts[1] = 'eyJzdWIiOiI5OTkifQ'
        for candidate in ('.'.join(parts), 'not-a-token', 'x'*4097):
            assert client.get('/v1/me', headers={'Authorization': 'Bearer '+candidate}).status_code == 401
        other = login(client)
        assert client.post('/v1/logout', headers=asha).status_code == 204
        assert client.get('/v1/me', headers=asha).status_code == 401
        assert client.get('/v1/me', headers=other).status_code == 200
        deleted = client.delete(url, headers=other)
        assert deleted.status_code == 204 and deleted.content == b''
        assert client.get(url, headers=other).status_code == 404
        schema = client.get('/openapi.json').json()
        assert '201' in schema['paths']['/v1/notes']['post']['responses']
        assert schema['components']['securitySchemes']['OAuth2PasswordBearer']['flows']['password']['tokenUrl'] == '/v1/token'
        for asset in ('/docs', '/assets/style.css', '/assets/explorer.js'):
            assert client.get(asset).status_code == 200
        explorer = client.get('/assets/explorer.js').text
        assert 'localStorage' not in explorer and '.innerHTML' not in explorer
        assert "fetch('/openapi.json')" in explorer and '[kept in this tab only]' in explorer

    with tempfile.TemporaryDirectory(prefix='studyhub-w39-restart-') as folder:
        with TestClient(create_app(folder)) as first:
            register(first); headers = login(first)
            first.post('/v1/notes', headers=headers, json={'title': 'Persistent', 'body': 'Across app reconstruction'})
        key_before = (Path(folder)/'signing.key').read_bytes()
        with TestClient(create_app(folder)) as second:
            assert second.get('/v1/notes', headers=headers).json()['items'][0]['title'] == 'Persistent'
            assert (Path(folder)/'signing.key').read_bytes() == key_before
        # A broken owned test key is refused, not silently replaced.
        (Path(folder)/'signing.key').write_bytes(b'bad')
        try:
            initialise(folder)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Invalid key must stop startup')
        assert (Path(folder)/'signing.key').read_bytes() == b'bad'
    with tempfile.TemporaryDirectory(prefix='studyhub-w39-schema-') as folder:
        path = Path(folder)/'notes.sqlite'
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE unrelated(value TEXT)'); db.execute("INSERT INTO unrelated VALUES('preserve')")
        db.commit(); db.close()
        before = path.read_bytes()
        try:
            initialise(folder)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Unfamiliar schema must stop startup')
        assert path.read_bytes() == before
    print('PASS: Week39 real private CRUD, strict models/PATCH False, sanitised errors, statuses/search/pagination, hashing, fixed JWT policy/failure cases/revocation, isolation/rollback, restart and unknown-schema preservation, generated schema and local explorer assets.')


if __name__ == '__main__':
    main()
