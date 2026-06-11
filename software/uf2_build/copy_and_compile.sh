#/bin/bash
set -e

echo "Copying EuroPi firmware and scripts to container..."
mkdir /micropython/ports/rp2/modules/contrib
mkdir /micropython/ports/rp2/modules/experimental
mkdir /micropython/ports/rp2/modules/tools
for pyfile in $(ls europi/software/firmware/*.py); do
    f=$(basename $pyfile)
    python3 /strip_python.py "$pyfile" "/micropython/ports/rp2/modules/$f"
done
for pyfile in $(ls europi/software/firmware/experimental/*.py); do
    f=$(basename $pyfile)
    python3 /strip_python.py "$pyfile" "/micropython/ports/rp2/modules/experimental/$f"
done
for pyfile in $(ls europi/software/firmware/tools/*.py); do
    f=$(basename $pyfile)
    python3 /strip_python.py "$pyfile" "/micropython/ports/rp2/modules/tools/$f"
done
for pyfile in $(ls europi/software/contrib/*.py); do
    f=$(basename $pyfile)
    python3 /strip_python.py "$pyfile" "/micropython/ports/rp2/modules/contrib/$f"
done

echo "Compiling micropython and firmware modules..."
cd /micropython/ports/rp2

# Pico W must be last; we need to remove some code to make it fit
# TODO: add RPI_PICO2_W once it's supported
BOARDS="RPI_PICO RPI_PICO2 RPI_PICO_W RPI_PICO2_W"

for b in $BOARDS; do
    echo "make BOARD=$b"
    make BOARD=$b
    echo "Moving firmware file to /europi/software/uf2_build/europi-$b-dev.uf2"
    mv build-$b/firmware.uf2 /europi/software/uf2_build/europi-$b-dev.uf2
done
