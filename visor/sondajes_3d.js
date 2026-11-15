(() => {
  'use strict';
  const source = window.G05_DRILLHOLES;
  const plot = document.getElementById('plot');
  let plotReady = false;
  const announceReady = () => {
    if (window.parent !== window) window.parent.postMessage({kind:'g05-sondajes-3d-ready'},'*');
  };
  addEventListener('message', event => {
    if (event.source === window.parent && event.data?.kind === 'g05-sondajes-3d-check' && plotReady) announceReady();
  });
  if (!window.Plotly || !source || source.hole_count !== 44 || source.holes.length !== 44) {
    document.getElementById('error').style.display = 'grid';
    return;
  }
  const colors = {C01:'#f48c52',C02:'#a1e1ad',C03:'#79c7dd'};
  const traces = source.holes.map(hole => ({
    type:'scatter3d',mode:'lines+markers',name:hole.id,showlegend:false,
    x:hole.x,y:hole.y,z:hole.z,
    line:{color:colors[hole.campaign],width:7},
    marker:{color:colors[hole.campaign],size:2.2,opacity:.85},
    text:hole.md.map(depth => `${hole.id} · MD ${depth.toFixed(2)} m`),
    hovertemplate:'%{text}<br>X %{x:.2f} m · Y %{y:.2f} m<br>Z %{z:.2f} m<extra></extra>'
  }));
  const collars = {
    type:'scatter3d',mode:'markers',showlegend:false,
    x:source.holes.map(h => h.x[0]),y:source.holes.map(h => h.y[0]),z:source.holes.map(h => h.z[0]),
    text:source.holes.map(h => `${h.id} · collar`),
    marker:{size:4.5,color:source.holes.map(h => colors[h.campaign]),line:{color:'#e9f7e9',width:1}},
    hovertemplate:'%{text}<br>X %{x:.2f} m · Y %{y:.2f} m<br>Z %{z:.2f} m<extra></extra>'
  };
  const axis = title => ({title:{text:title,font:{size:10,color:'#a1c1b5'}},showbackground:true,backgroundcolor:'#142b2b',gridcolor:'#34534d',zerolinecolor:'#34534d',showticklabels:false,showspikes:false});
  Plotly.newPlot(plot,[...traces,collars],{
    margin:{l:0,r:0,t:0,b:0},paper_bgcolor:'#102124',plot_bgcolor:'#102124',showlegend:false,
    scene:{xaxis:axis('E'),yaxis:axis('N'),zaxis:axis('Z'),aspectmode:'data',camera:{eye:{x:1.45,y:-1.65,z:.95}},dragmode:'orbit'}
  },{responsive:true,displayModeBar:false,scrollZoom:true}).then(() => {
    plotReady = true;
    announceReady();
  }).catch(() => { document.getElementById('error').style.display = 'grid'; });
})();
