// Fictional prepared records only. IPs use documentation address ranges.
const events=[
 {record:'L01',source:'auth',event_id:'A01',event_time:'2026-10-01T09:00:00+09:00',received_time:'2026-10-01T00:00:05Z',account:'maya',action:'login.failed',result:'rejected',source_ip:'192.0.2.40'},
 {record:'L02',source:'auth',event_id:'A02',event_time:'2026-10-01T00:01:00Z',received_time:'2026-10-01T00:01:04Z',account:'maya',action:'login.failed',result:'rejected',source_ip:'192.0.2.40'},
 {record:'L03',source:'auth',event_id:'A03',event_time:'2026-10-01T09:02:00+09:00',received_time:'2026-10-01T00:02:06Z',account:'maya',action:'login.failed',result:'rejected',source_ip:'192.0.2.40'},
 {record:'L04',source:'auth',event_id:'A03',event_time:'2026-10-01T09:02:00+09:00',received_time:'2026-10-01T00:03:00Z',account:'maya',action:'login.failed',result:'rejected',source_ip:'192.0.2.40',annotation:'Repeated delivery of A03, not another failed login'},
 {record:'L05',source:'auth',event_id:'A10',event_time:'2026-10-01T00:03:00Z',received_time:'2026-10-01T00:03:02Z',account:'maya',action:'login.success',result:'accepted',source_ip:'198.51.100.20',correlation_ref:'C-7'},
 {record:'L06',source:'application',event_id:'P01',event_time:'2026-10-01T00:04:30Z',received_time:'2026-10-01T00:04:31Z',account:'maya',action:'note.edit',resource:'N2',resource_owner:'ravi',status:403,result:'owner_check_refused',write_performed:false,correlation_ref:'C-7'},
 {record:'L07',source:'application',event_id:'P02',event_time:'2026-10-01T09:05:00+09:00',received_time:'2026-10-01T00:05:02Z',account:'maya',action:'note.edit',resource:'N1',resource_owner:'maya',status:200,result:'persisted',write_performed:true,correlation_ref:'C-7'},
 {record:'L08',source:'endpoint',event_id:'E01',event_time:'2026-10-01T00:06:00Z',received_time:'2026-10-01T00:06:10Z',asset:'LAB-A',action:'agent.heartbeat',result:'received'},
 {record:'L09',source:'network',event_id:'N01',event_time:'2026-10-01T00:03:10Z',received_time:'2026-10-01T00:06:20Z',action:'connection.allowed',result:'allowed',source_ip:'198.51.100.20',destination:'APP-A',destination_port:443},
 {record:'L10',source:'alert',event_id:'Z01',event_time:'2026-10-01T00:07:00Z',received_time:'2026-10-01T00:07:01Z',action:'rule.threshold',result:'review_required',account:'maya',rule:'At least3 unique auth failures in [00:00,00:03) UTC',observed_event_ids:['A01','A02','A03'],annotation:'A04 had not arrived; alert is not another failed login'},
 {record:'L11',source:'legacy-export',event_id:'X01',event_time:'2026-10-01 09:01:30',received_time:'2026-10-01T00:08:00Z',account:'maya',action:'legacy.note_seen',result:'unknown',annotation:'Source timezone is undocumented; do not infer UTC/Japan from clock text'},
 {record:'L12',source:'auth',event_id:'A04',event_time:'2026-10-01T00:01:30Z',received_time:'2026-10-01T00:08:30Z',account:'maya',action:'login.failed',result:'rejected',source_ip:'192.0.2.40',annotation:'Late delivery; earlier event time than receipt time suggests'}
];
const context={
 title:'Fictional Week7 case: a repeated-login alert and note actions',
 scope:'Prepared sample records, not any real account/device/service observation',
 limitations:[
  'Record order is collector delivery order, not chronological event order.',
  'Event identities are source + event_id; L04 repeats auth A03.',
  'Offset-bearing source clocks are assumed correct only for this worksheet; a real clock needs verification.',
  'X01 has no documented timezone, so its event position in UTC remains unknown.',
  'C-7 is a public non-credential correlation label, not a live session/token value.',
  'Documentation IPs do not identify a real sender; IP/account labels do not prove a human actor.',
  'A scheduled class job might use 192.0.2.40, but its run/credential state has not been verified.',
  'No stored note contents, passwords, tokens, malware artefacts or complete access history are supplied.',
  'Application logs report refusal/persistence; independent stored-state evidence would strengthen verification.',
  'The exercise establishes investigation questions, not confirmed takeover, exfiltration or attribution.'
 ]
};
module.exports={events,context};
