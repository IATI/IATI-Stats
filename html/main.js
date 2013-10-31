$(document).ready(function() {
    var dates, data, most_recent_commit;
    create_stat_element = function (stat) {
        click_stat = function(e, key) {
            $('#chart').html('')
            var chartdata = [];
            var formatDate = d3.time.format.iso;
            var cdata = [];
            for (commit in data[stat]) {
                var cdatavalue;
                console.log(key, data[stat][commit])
                if (key === undefined)
                    cdatavalue = data[stat][commit]
                else
                    cdatavalue = data[stat][commit][key]
                if (cdatavalue === undefined)
                    cdatavalue = 0
                cdata.push([
                    formatDate.parse(dates[commit]).getTime() / 1000,
                    cdatavalue 
                ]);
            }
            cdata.sort();
            for (var i=0; i<cdata.length; i++) {
                chartdata.push({x:cdata[i][0], y:cdata[i][1]});
            }
            //console.log(chartdata);

            var min = Number.MAX_VALUE;
            var max = Number.MIN_VALUE;
            for (i = 0; i < chartdata.length; i++) {
              min = Math.min(min, chartdata[i].y);
              max = Math.max(max, chartdata[i].y);
            }
            //var linearScale = d3.scale.linear().domain([min, max]);

            var graph = new Rickshaw.Graph( {
                element: document.querySelector("#chart"), 
                width: 600, 
                height: 400, 
                renderer: 'line',
                interpolvalueation: 'linear',
                series: [{
                    color: 'steelblue',
                    data: chartdata,
                    //scale: linearScale
                }]
            });
            var xAxis = new Rickshaw.Graph.Axis.Time( { graph: graph } );
            var yAxis = new Rickshaw.Graph.Axis.Y({//.Scaled( 
                graph: graph,
                tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
                //scale: linearScale
                } );
            new Rickshaw.Graph.HoverDetail(
            {
              graph: graph
            }); 
            graph.render();

        };
        var list_item = $('<li>');
        var recent_data = data[stat][most_recent_commit]
        if (typeof recent_data === "number") {
            list_item.append($('<a href="#">'+stat+'</a>').click(click_stat));
            list_item.append(' '+recent_data);
        }
        else if (typeof recent_data === "object") {
            var table = $('<table style="display:none">')
            list_item.append($('<a href="#">'+stat+'</a>').click(function () { table.toggle() }));
            table.stupidtable();
            table.append('<thead><tr><th data-sort="string">key</th><th data-sort="int">value</th></tr></thead>')
            var tbody = $('<tbody/>');
            table.append(tbody)
            list_item.append(table);
            create_table_row = function (key, click_stat) {
                var key_link = $('<a href="#">'+key+'</a>').click(function (e) { click_stat(e,key); });
                tbody.append($('<tr>').append($('<td>').append(key_link)).append($('<td>'+recent_data[key]+'</td></tr>')));
            }
            for (var key in recent_data) {
                create_table_row(key, click_stat);
            }
        }
        $('#list').append(list_item);
    }

    $.when( $.getJSON('../gitdate.json'), $.getJSON('../gitaggregate.json') ).done(function (d1, d2) {
        dates = d1[0]; data = d2[0];
        most_recent_commit = _.last(_.sortBy(_.pairs(dates), function(d) {return d[1]}))[0]
        for (var key in data) {
            create_stat_element(key);
        }
    });
});

