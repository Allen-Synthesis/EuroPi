#/bin/bash
set -e

echo "Copying EuroPi firmware and scripts to container..."
mkdir /micropython/ports/rp2/modules/contrib
mkdir /micropython/ports/rp2/modules/experimental
mkdir /micropython/ports/rp2/modules/tools

# Directories we copy stripped Python files _from_
SRC_DIRS=(europi/software/firmware
europi/software/firmware/experimental
europi/software/firmware/tools
europi/software/contrib)

# Directories we copy stripped Python files _to_
# Order must match SRC_DIRS
DST_DIRS=(/micropython/ports/rp2/modules
/micropython/ports/rp2/modules/experimental
/micropython/ports/rp2/modules/tools
/micropython/ports/rp2/modules/contrib)

for i in ${!SRC_DIRS[@]}; do
    src_dir=${SRC_DIRS[i]}
    dst_dir=${DST_DIRS[i]}

    for pyfile in $(ls ${src_dir}/*.py); do
        f=$(basename $pyfile)
        echo "Stripping $pyfile -> $dst_dir"
        python3 /strip_python.py $pyfile ${dst_dir}/$f
    done
done

echo "Compiling micropython and firmware modules..."
cd /micropython/ports/rp2

# Pico W must be last; we need to remove some code to make it fit
# TODO: What do we actually need to remove?
BOARDS="RPI_PICO2 RPI_PICO RPI_PICO2_W RPI_PICO_W"

for b in $BOARDS; do
    echo "make BOARD=$b"
    make BOARD=$b
    echo "Moving firmware file to /europi/software/uf2_build/europi-$b-dev.uf2"
    mv build-$b/firmware.uf2 /europi/software/uf2_build/europi-$b-dev.uf2
done
