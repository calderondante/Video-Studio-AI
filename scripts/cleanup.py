"""Remove only stale ASR scratch directories, after validating the final media."""
import argparse
from pathlib import Path
import shutil
import time
from common import validate
p=argparse.ArgumentParser();p.add_argument('--validated-output',required=True);p.add_argument('--job-dir',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
validate(a.validated_output)
root=Path('work').resolve();job=Path(a.job_dir).resolve()
if not job.is_relative_to(root) or job==root:raise ValueError('Choose a job directory inside work/')
for candidate in job.glob('studio-asr-*'):
    if not candidate.is_symlink() and candidate.is_dir() and time.time()-candidate.stat().st_mtime>86400:
        print(('REMOVE ' if a.apply else 'DRY RUN ')+str(candidate))
        if a.apply:shutil.rmtree(candidate)
