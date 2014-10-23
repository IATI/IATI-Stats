mkdir schemas
cd schemas
for v in 1.01 1.02 1.03 1.04 1.05; do
    git clone https://github.com/IATI/IATI-Schemas.git $v
    cd $v
    git checkout version-$v
    cd ..
done
