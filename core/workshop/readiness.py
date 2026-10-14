"""Read-only app readiness without optional Bambu or printer operations."""
import sys
import subprocess
from pathlib import Path
from core.environment import dependency_checks
from core.workflow.openscad import find_openscad, openscad_version
from core.workshop.app_build import app_build_check

def check_readiness(root:Path):
    checks=[{'name':'Python','status':'pass' if (3,12)<=sys.version_info[:2]<=(3,13) else 'fail','detail':sys.version.split()[0]}]
    checks.append({'name':'worker runtime','required':True,'status':'pass' if sys.platform=='win32' else 'fail',
                   'detail':'Windows process containment is required for Workshop background workers.',
                   'corrective_action':'Launch Print Workshop on Windows. Portable CLI validation remains available on other platforms.'})
    checks.extend(dependency_checks(root))
    try:
        executable=find_openscad()
        checks.append({'name':'OpenSCAD','status':'pass','detail':openscad_version(executable),'path':str(executable)})
    except (OSError,RuntimeError,subprocess.TimeoutExpired) as exc:
        checks.append({'name':'OpenSCAD','status':'fail','detail':str(exc),'corrective_action':'Select an installed compiler using OPENSCAD_PATH.'})
    checks.append(app_build_check(root))
    return {'ready':all(item['status']=='pass' for item in checks),'interpreter':sys.executable,'checks':checks,'printer_connection':'not attempted'}
