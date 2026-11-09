#!/usr/bin/env python3
"""Build using Python, librsvg, JDK, and the official Android SDK tools."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads((ROOT / 'version.json').read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--sdk', default=os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT'))
parser.add_argument('--jobs', type=int, default=4)
parser.add_argument('--keystore', type=Path, help='Release keystore. Password is read from SORCERY_STORE_PASSWORD.')
parser.add_argument('--alias', default='sorcery')
args = parser.parse_args()
if not args.sdk:
    parser.error('Provide --sdk or set ANDROID_HOME')
sdk = Path(args.sdk)
tools = sdk / 'build-tools/37.0.0'
android = sdk / 'platforms/android-35/android.jar'
for executable in ['javac', 'keytool', 'rsvg-convert']:
    if not shutil.which(executable):
        parser.error('Required executable: ' + executable)
for path in [android, tools / 'aapt2', tools / 'd8', tools / 'apksigner', tools / 'zipalign']:
    if not path.exists():
        parser.error('Required SDK file: ' + str(path))


def run(command, **kwargs):
    subprocess.run([str(x) for x in command], cwd=ROOT, check=True, **kwargs)


run([sys.executable, 'tools/generate.py'])
run([sys.executable, 'tools/validate.py'])
build = ROOT / 'build'
if build.exists():
    shutil.rmtree(build)
for directory in ['res/drawable-nodpi', 'res/xml', 'assets', 'classes', 'dex']:
    (build / directory).mkdir(parents=True, exist_ok=True)
for png in (ROOT / 'artwork/original').glob('*.png'):
    shutil.copyfile(png, build / 'res/drawable-nodpi' / png.name)
for xml in (ROOT / 'app/res/xml').glob('*.xml'):
    shutil.copyfile(xml, build / 'res/xml' / xml.name)
shutil.copytree(ROOT / 'app/assets', build / 'assets', dirs_exist_ok=True)
for filename in ['LICENSE', 'THIRD_PARTY_NOTICES.md']:
    shutil.copyfile(ROOT / filename, build / 'assets' / filename)
shutil.copytree(ROOT / 'licenses', build / 'assets/licenses')


def render(source):
    target = build / 'res/drawable-nodpi' / (source.stem + '.png')
    if source.suffix == '.png':
        from PIL import Image
        with Image.open(source) as image:
            image.convert('RGBA').resize((192, 192), Image.Resampling.LANCZOS).save(target)
        return
    run(['rsvg-convert', '--width', '192', '--height', '192', '--output', target, source], stdout=subprocess.DEVNULL)


with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
    catalog = json.loads((ROOT / 'catalog/icons.json').read_text())
    sources = [ROOT / 'artwork/icons' / (item['id'] + '.' + item.get('format', 'svg')) for item in catalog]
    list(executor.map(render, sources))
# The app mark is a small tree cut from paper, distinct from app brand logos.
render(ROOT / 'artwork/rebirth_app_icon.svg')
for source in (ROOT / 'artwork/fallback').glob('*.svg'):
    render(source)
run([tools / 'aapt2', 'compile', '--no-crunch', '--dir', build / 'res', '-o', build / 'compiled.zip'])
run([tools / 'aapt2', 'link', '-o', build / 'resources.apk', '-I', android,
     '--manifest', ROOT / 'app/AndroidManifest.xml', '-A', build / 'assets',
     '--min-sdk-version', VERSION['min_sdk'], '--target-sdk-version', VERSION['target_sdk'],
     '--version-code', VERSION['code'], '--version-name', VERSION['name'],
     build / 'compiled.zip'])
java = list((ROOT / 'app/src').rglob('*.java'))
run(['javac', '-encoding', 'UTF-8', '--release', '8', '-classpath', android,
     '-d', build / 'classes', *java])
run([tools / 'd8', '--lib', android, '--min-api', VERSION['min_sdk'], '--output', build / 'dex',
     *sorted((build / 'classes').rglob('*.class'))])
unsigned = build / 'unsigned.apk'
shutil.copyfile(build / 'resources.apk', unsigned)
with zipfile.ZipFile(unsigned, 'a', zipfile.ZIP_DEFLATED) as apk:
    for dex in (build / 'dex').glob('*.dex'):
        apk.write(dex, dex.name)
run([tools / 'zipalign', '-f', '-p', '4', unsigned, build / 'aligned.apk'])

keystore = args.keystore
if keystore is None:
    keystore = ROOT / '.local/debug.p12'
    keystore.parent.mkdir(exist_ok=True)
    os.environ['SORCERY_STORE_PASSWORD'] = 'android'
    if not keystore.exists():
        run(['keytool', '-genkeypair', '-keystore', keystore, '-storetype', 'PKCS12',
             '-storepass:env', 'SORCERY_STORE_PASSWORD', '-keypass:env', 'SORCERY_STORE_PASSWORD',
             '-alias', args.alias, '-keyalg', 'RSA', '-keysize', '3072', '-validity', '10000',
             '-dname', 'CN=Sorcery Rebirth Development'])
if not os.environ.get('SORCERY_STORE_PASSWORD'):
    parser.error('Set SORCERY_STORE_PASSWORD for the release keystore')
dist = ROOT / 'dist'
dist.mkdir(exist_ok=True)
output = dist / ('Sorcery_rebirth-' + VERSION['name'] + '.apk')
run([tools / 'apksigner', 'sign', '--ks', keystore, '--ks-key-alias', args.alias,
     '--ks-pass', 'env:SORCERY_STORE_PASSWORD', '--out', output, build / 'aligned.apk'])
run([tools / 'apksigner', 'verify', '--verbose', '--print-certs', output])
digest = hashlib.sha256(output.read_bytes()).hexdigest()
(dist / 'SHA256SUMS').write_text(digest + '  ' + output.name + '\n')
print(output.name, output.stat().st_size, digest)
