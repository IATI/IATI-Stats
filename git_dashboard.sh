echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Starting Stats generation"
echo "========="

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running general stats"
echo "========="
GITOUT_SKIP_INCOMMITSDIR=1 ./git.sh --stats-module stats.analytics $@
