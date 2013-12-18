mkdir out-ti
for f in data-ti/*; do
    rm -r out/*
    rm -r aggregated/*
    python loop.py --stats-module transparency_indicator --data $f
    python aggregate.py --stats-module transparency_indicator
    mv aggregated.json out-ti/`basename $f`.json
    mv aggregated out-ti/`basename $f`
done
