if [ ! -d IATI-Codelists ]; then
    git clone https://github.com/IATI/IATI-Codelists.git
fi
cd IATI-Codelists
git checkout version-1.05 > /dev/null
git pull > /dev/null
./gen.sh
