### Development environment setup.

Clone `cracknuts` code to local.

```shell
git clone https://github.com/cracknuts-team/cracknuts.git
```

Create a virtual environment and then install cracknuts in *editable* mode.

On Linux:

```shell
cd cracknuts
python3 -m venv --prompt cracknuts .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows:

```shell
cd cracknuts
python -m venv --prompt cracknuts .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

You then need to install the JavaScript dependencies and run the development server.

```sh
cd jupyter_frontend
pnpm i
```

Then you can run dev mode at developing.

```sh
npm run dev
```

To enable `HMR` you should set environment `ANYWIDGET_HMR=1`  

```shell
# powershell
$env:ANYWIDGET_HMR=1
```

```shell
# bash
ANYWIDGET_HMR=1 jupyter lab
```
