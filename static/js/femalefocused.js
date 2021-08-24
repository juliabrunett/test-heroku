d3.json("/api/female_led").then((data, err) => {
  var femaledata = data;

function buildBubble() {
  console.log(femaledata)
  

  // First 20 records - get data needed from json
  var budget = [];
  var revenue = [];
  var similarity = [];
  var title = [];
  var genres = [];
  var director = [];
  var release = [];
  var runtime = [];

  for (var i=0; i<20; i++) {
    budget.push(femaledata[i].budget);
    revenue.push(femaledata[i].revenue);
    similarity.push(Math.pow(femaledata[i].similarity_score*50,2));
    title.push(femaledata[i].title);
    genres.push(femaledata[i].genres);
    director.push(femaledata[i].director);
    release.push(femaledata[i].release_date);
    runtime.push(femaledata[i].runtime);
  }
  console.log(similarity)

  // Build BUBBLE
  var Hoverinfo = []
  for (i=0;i<director.length;i++){
    p = {"Title":title[i], "Genre": genres[i], "Director":director[i],
        "Release_Date":release[i],"Run_Time":runtime[i]+" min."}
    Hoverinfo.push(p)
  }
  var data = [{
    x: revenue,
    y: budget,
    text: Hoverinfo,
    mode: 'markers',
    marker: {
      size: similarity,
      color: revenue,
      colorscale: "RdBu"
    },
    hovertemplate:
    "<b>Title:</b> %{text.Title}<br><b>Genre:</b> %{text.Genre}<br><b>Director:</b> %{text.Director}<br><b>Release Date:</b> %{text.Release_Date} <br> <b>Run Time:</b>%{text.Run_Time}<extra></extra>"
  }];
  var layout = {
    title: `Female Lead or Directed Film Recommendations`,
    font: { size: 13 },
    xaxis: { title: "Revenue" },
    yaxis: {title: "Budget"}
  };
  Plotly.newPlot('bubble', data, layout); 
}
// -------------------------------------------------- //
// Build Table
//Get a reference to the table body
var tbody = d3.select("tbody");

function buildTable() {
  d3.json("/api/similarity_scores").then((data, err) => {
    if (err) throw err;
    console.log(data);

    //Get first 15 records
    const slicedArray = data.slice(0, 10);
    console.log(slicedArray);

    var newData = [];
    slicedArray.forEach(obj => { 
    newData.push({"title": obj.title, "genres": obj.genres, "director": obj.director, "cast": obj.cast, "release_date": obj.release_date, 
                  "runtime": obj.runtime, "budget": obj.budget, "revenue": obj.revenue});  
    });
    console.log(newData);

    newData.forEach(obj => {
      var row = tbody.append("tr");
      Object.entries(obj).forEach(([key, value]) => row.append("td").text(value));
    });  
  });
}   
//------------------------------------------------------------
buildBubble();
//buildTable();

});