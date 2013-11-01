mkdir schemas
cd schemas
for v in 1.01 1.02 1.03; do
    git clone https://github.com/IATI/IATI-Schemas.git $v
    cd $v
    git checkout v$v
    cd ..
done
