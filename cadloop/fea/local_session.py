"""Run a local MAPDL session and always close the solver we launched."""
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def local_mapdl(run_directory, jobname='analysis'):
    from ansys.mapdl.core import launch_mapdl
    directory=Path(run_directory)
    directory.mkdir(parents=True,exist_ok=True)
    mapdl=launch_mapdl(
        exec_file=r'C:\Program Files\ANSYS Inc\ANSYS Student\v261\ansys\bin\winx64\ANSYS261.exe',
        run_location=str(directory),jobname=jobname,mode='grpc',start_instance=True,
        nproc=2,ram=4096,additional_switches='-smp',start_timeout=120,
        log_apdl=str(directory/'commands.inp'),cleanup_on_exit=True)
    try:
        yield mapdl
    finally:
        mapdl.exit()
