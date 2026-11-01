"""Compila un archivo MQL5 (.mq5) o MQL4 (.mq4) con el MetaEditor instalado en este computador
y explica el resultado en español.

Uso:
    python .claude/skills/programador/compilar_mql.py robots/<idea>_mt5_estrategia.mq5
    python .claude/skills/programador/compilar_mql.py robots/<idea>_mt4_estrategia.mq4
    (opcional) --metaeditor "C:/ruta/metaeditor64.exe"  si no lo encuentra solo

Qué hace: busca el MetaEditor de MetaTrader 5 (para .mq5) o de MetaTrader 4 (para .mq4), compila
el archivo con su carpeta de librerías (Include) y lee el registro de la compilación.
Salida: COMPILA (0 errores) o NO COMPILA, con cada error y aviso: línea, columna y mensaje.
Código de salida: 0 compila · 1 hay errores · 2 no se encontró MetaEditor o el archivo.
No toca la lógica del código: solo compila. El .ex5/.ex4 queda junto al archivo y no se sube a
GitHub (.gitignore).
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile

LINEA = re.compile(r'\((\d+),(\d+)\)\s*:\s*(error|warning)\s*(\d+)?\s*:?\s*(.*)', re.I)
RESUMEN = re.compile(r'(\d+)\s+errors?,\s*(\d+)\s+warnings?', re.I)


def salir(msg, codigo=2):
    print(msg)
    sys.exit(codigo)


def candidatos(version):
    """Rutas posibles del MetaEditor: instalaciones normales y las que guardan las carpetas de datos."""
    exe = ['metaeditor64.exe', 'MetaEditor64.exe'] if version == 5 else ['metaeditor.exe', 'MetaEditor.exe']
    bases = [os.environ.get(v, '') for v in ('ProgramFiles', 'ProgramFiles(x86)', 'ProgramW6432')]
    rutas = []
    for b in filter(None, bases):
        for e in exe:
            rutas += glob.glob(os.path.join(b, '*', e)) + glob.glob(os.path.join(b, '*', '*', e))
    # cada terminal deja en su carpeta de datos un origin.txt con la carpeta donde se instaló
    for origen in glob.glob(os.path.join(os.environ.get('APPDATA', ''), 'MetaQuotes', 'Terminal', '*', 'origin.txt')):
        try:
            carpeta = open(origen, encoding='utf-16').read().strip()
        except (UnicodeError, OSError):
            try:
                carpeta = open(origen, encoding='utf-8', errors='ignore').read().strip()
            except OSError:
                continue
        rutas += [os.path.join(carpeta, e) for e in exe]
    vistas, unicas = set(), []
    for r in rutas:
        k = os.path.normcase(os.path.abspath(r))
        if os.path.isfile(r) and k not in vistas:
            vistas.add(k)
            unicas.append(r)
    return unicas


def carpeta_mql(metaeditor, version):
    """La carpeta MQL5/MQL4 con las librerías estándar (Include) de ese terminal."""
    sub = 'MQL5' if version == 5 else 'MQL4'
    instalacion = os.path.dirname(os.path.abspath(metaeditor))
    for origen in glob.glob(os.path.join(os.environ.get('APPDATA', ''), 'MetaQuotes', 'Terminal', '*', 'origin.txt')):
        for cod in ('utf-16', 'utf-8'):
            try:
                if os.path.normcase(open(origen, encoding=cod).read().strip()) == os.path.normcase(instalacion):
                    datos = os.path.join(os.path.dirname(origen), sub)
                    if os.path.isdir(os.path.join(datos, 'Include')):
                        return datos
                break
            except (UnicodeError, OSError):
                continue
    propia = os.path.join(instalacion, sub)          # instalación portátil
    return propia if os.path.isdir(os.path.join(propia, 'Include')) else None


def leer_log(ruta):
    datos = open(ruta, 'rb').read()
    for cod in ('utf-16', 'utf-8-sig', 'cp1252'):
        try:
            texto = datos.decode(cod)
            if 'rror' in texto or 'esult' in texto or not datos.startswith(b'\xff\xfe'):
                return texto
        except UnicodeError:
            continue
    return datos.decode('latin-1')


def main():
    a = argparse.ArgumentParser(description='Compila un .mq5 o .mq4 con MetaEditor y explica los errores.')
    a.add_argument('archivo', help='el .mq5 o .mq4 a compilar')
    a.add_argument('--metaeditor', help='ruta de metaeditor64.exe (MT5) o metaeditor.exe (MT4)')
    o = a.parse_args()

    archivo = os.path.abspath(o.archivo)
    ext = os.path.splitext(archivo)[1].lower()
    if ext not in ('.mq5', '.mq4'):
        salir('El archivo tiene que ser .mq5 (MetaTrader 5) o .mq4 (MetaTrader 4).')
    if not os.path.isfile(archivo):
        salir(f'No encuentro el archivo {o.archivo}.')
    version = 5 if ext == '.mq5' else 4
    if sys.platform != 'win32':
        salir('MetaEditor solo funciona en Windows: compílalo en tu MetaTrader y trae los errores.')

    if o.metaeditor:
        metaeditor = o.metaeditor
        if not os.path.isfile(metaeditor):
            salir(f'No encuentro {metaeditor}.')
    else:
        hallados = candidatos(version)
        if not hallados:
            salir(f'No encontré el MetaEditor de MetaTrader {version} en este computador. Si lo tienes '
                  f'instalado en otra carpeta, pásalo con --metaeditor. Si no, compílalo tú en MetaTrader '
                  f'{version} (F4 → Compilar) y trae los errores.')
        metaeditor = hallados[0]

    inc = carpeta_mql(metaeditor, version)
    log = os.path.join(tempfile.gettempdir(), 'compilar_mql_' + os.path.basename(archivo) + '.log')
    if os.path.exists(log):
        os.remove(log)
    # MetaEditor quiere las comillas solo alrededor de la ruta (/compile:"C:\mi carpeta\x.mq5"):
    # con una lista, Python las pondría alrededor de todo y fallaría con espacios en la ruta.
    cmd = f'"{metaeditor}" /compile:"{archivo}" /log:"{log}"'
    if inc:
        cmd += f' /inc:"{inc}"'
    try:
        subprocess.run(cmd, timeout=180, capture_output=True)
    except subprocess.TimeoutExpired:
        salir('MetaEditor tardó más de 3 minutos y lo detuve. Ábrelo a mano y compila desde ahí.')
    except OSError as e:
        salir(f'No pude abrir MetaEditor ({e}). Compílalo tú en MetaTrader {version} y trae los errores.')

    if not os.path.isfile(log):
        salir('MetaEditor no dejó registro de la compilación. Compílalo a mano (F4 → Compilar) y trae los errores.')
    texto = leer_log(log)
    errores, avisos = [], []
    for linea in texto.splitlines():
        m = LINEA.search(linea)
        if m:
            fila, col, tipo, num, msg = m.groups()
            (errores if tipo.lower() == 'error' else avisos).append(
                f'  línea {fila}, columna {col}: {msg.strip()}' + (f' (código {num})' if num else ''))
    r = RESUMEN.search(texto)
    n_err = int(r.group(1)) if r else len(errores)

    print(f'MetaEditor: {metaeditor}')
    print(f'Librerías (Include): {inc or "las del propio MetaEditor"}')
    if n_err == 0 and r:
        print(f'\nCOMPILA · 0 errores · {len(avisos)} avisos')
    elif n_err == 0:
        print('\nNo pude leer el resultado del registro. Revisa a mano:\n' + texto[-1500:])
        sys.exit(1)
    else:
        print(f'\nNO COMPILA · {n_err} errores · {len(avisos)} avisos')
    if errores:
        print('Errores:\n' + '\n'.join(errores))
    if avisos:
        print('Avisos (no impiden compilar, pero revísalos):\n' + '\n'.join(avisos))
    sys.exit(0 if n_err == 0 and r else 1)


if __name__ == '__main__':
    main()
