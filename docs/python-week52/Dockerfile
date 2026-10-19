FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home learner
COPY capstone ./capstone
RUN mkdir /app/data && chown -R learner:learner /app
USER learner
ENV CAPSTONE_DB=/app/data/studylog.sqlite
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "capstone.main:app", "--host", "0.0.0.0", "--port", "8000"]
