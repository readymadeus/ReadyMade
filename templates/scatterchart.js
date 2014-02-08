$.ajax({
  type: 'GET',
  url: '../static/files/uploads/coffeedat.json',
  async: false,
  contentType:"jsonp",
  dataType: 'jsonp',
  
});

    
    var data = [];
    for(i=0;i<jsondat.length;i++){
          xval=jsondat[i][scatterx];
          yval=jsondat[i][scattery];
          if(xval!=null && yval!=null){
            data.push([xval,yval]);
          }
    }
       
    var margin = {top: 20, right: 15, bottom: 60, left: 60}
      , width = 960 - margin.left - margin.right
      , height = 500 - margin.top - margin.bottom;
    
    var x = d3.scale.linear()
              .domain([0, d3.max(data, function(d) { return d[0]; })])
              .range([ 0, width ]);
    
    var y = d3.scale.linear()
    	      .domain([0, d3.max(data, function(d) { return d[1]; })])
    	      .range([ height, 0 ]);
 
    var chart = d3.select('div#content')
	.append('svg:svg')
	.attr('width', width + margin.right + margin.left)
	.attr('height', height + margin.top + margin.bottom)
	.attr('class', 'chart');
 
  var div=d3.select('div#content').append("div")
  .attr('class','tooltip')
  .style("opacity",0);

    var main = chart.append('g')
	.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
	.attr('width', width)
	.attr('height', height)
	.attr('class', 'main')   
        
    // draw the x axis
    var xAxis = d3.svg.axis()
	.scale(x)
	.orient('bottom');

    main.append('g')
	.attr('transform', 'translate(0,' + height + ')')
	.attr('class', 'main axis date')
	.call(xAxis);

    // draw the y axis
    var yAxis = d3.svg.axis()
	.scale(y)
	.orient('left');

    main.append('g')
	.attr('transform', 'translate(0,0)')
	.attr('class', 'main axis date')
	.call(yAxis);

    var g = main.append("svg:g"); 
    
    g.selectAll("scatter-dots")
      .data(data)
      .enter().append("svg:circle")
          .attr("cx", function (d,i) { return x(d[0]); } )
          .attr("cy", function (d) { return y(d[1]); } )
          .attr("r", 8)
          .on('mouseover',function(d){
            d3.select(this)
            .attr("r",16)
            .style("fill","orange");

            div.transition()
            .duration(200)
            .style("opacity",0.9);

            div.html(d)
              .style("left", (d3.event.pageX) + "px")     
              .style("top", (d3.event.pageY - 28) + "px");
          })
          .on('mouseout',function(d){
            d3.select(this)
            .attr("r",8)
            .style("fill","steelblue");

            div.transition()        
                .duration(500)      
                .style("opacity", 0);
          });

    g.append("text")
    .attr("class","xlabel")
    .attr("text-anchor","center")
    .attr("x",width-300)
    .attr("y",height-50)
    .text(scatterx);

     g.append("text")
    .attr("class","ylabel")
    .attr("text-anchor","center")
    .attr("x",8)
    .attr("y",-5)
    .text(scattery);


