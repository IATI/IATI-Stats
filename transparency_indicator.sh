mkdir out-ti out-ti-err
for f in data-ti/*; do
    rm -r out/*
    rm -r aggregated/*
    python loop.py --stats-module transparency_indicator --data $f > out-ti-err/`basename $f`_loop
    python aggregate.py --stats-module transparency_indicator > out-ti-err/`basename $f`_aggregate
    mv aggregated.json out-ti/`basename $f`.json
    mv aggregated out-ti/`basename $f`
done
