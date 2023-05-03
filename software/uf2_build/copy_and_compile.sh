#/bin/sh
set -e

echo "Copying EuroPi firmware and scripts to container..."
mkdir micropython/ports/rp2/modules/contrib
mkdir micropython/ports/rp2/modules/experimental
cp -r europi/software/firmware/*.py micropython/ports/rp2/modules
cp -r europi/software/firmware/experimental/*.py micropython/ports/rp2/modules/experimental
cp -r europi/software/contrib/*.py micropython/ports/rp2/modules/contrib

echo "Compiling micropython and firmware modules..."
cd micropython/ports/rp2
make

echo "Copying firmware file to /europi/software/uf2_build/europi-dev.uf2"
cp build-PICO/firmware.uf2 /europi/software/uf2_build/europi-dev.uf2
