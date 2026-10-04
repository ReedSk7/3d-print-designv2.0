from core.workshop.jobs import JobStore

def test_restart_marks_active_jobs_interrupted(tmp_path):
    first=JobStore(tmp_path/'jobs.json'); first.update('sample',status='running',action='generate')
    second=JobStore(tmp_path/'jobs.json')
    assert second.records['sample']['status']=='interrupted'
    assert 'Inspect' in second.records['sample']['error']
