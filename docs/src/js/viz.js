// setup API options
const options = {
    config: {
      // Vega-Lite default configuration
    },
    init: (view) => {
      // initialize tooltip handler
      view.tooltip(new vegaTooltip.Handler().call);
    },
    view: {
      // view constructor options
      // remove the loader if you don't want to default to vega-datasets!
      loader: vega.loader({
        baseURL: "https://cdn.jsdelivr.net/npm/vega-datasets@2/",
      }),
      renderer: "canvas",
    },
  };

console.log(window.location.pathname)
// register vega and vega-lite with the API
vl.register(vega, vegaLite, options); 

var data = ({
    "Gradient": [98.12351543942992, 98.45605700712589, 97.6326207442597, 96.66666666666667, 94.98020585906572, 93.38083927157561, 90.61757719714964, 85.45526524148852, 5.7007125890736345],
    "L2": [98.12351543942992, 98.18685669041963, 97.1021377672209, 94.90102929532858, 93.83214568487728, 88.9865399841647, 5.7007125890736345, 5.225653206650831, 5.225653206650831],
    "HRank": [98.12351543942992, 98.59065716547902, 94.34679334916865, 90.07917656373714, 87.30007917656374, 87.22882026920031, 80.02375296912113, 56.365795724465556, 5.7007125890736345],
    "K-means": [98.12351543942992, 98.25811559778306, 97.72763262074426, 96.14410134600158, 96.53998416468725, 94.89311163895486, 91.60728424386382, 85.17814726840855, 5.938242280285036]
  });

// potentially buggy 2nd trial
//   grad = [98.3372921615202, 98.06017418844023, 97.8068091844814, 95.91448931116389, 95.93824228028504, 92.39904988123516, 87.71179730799683, 84.0221694378464, 45.24940617577197]
  
//   l2 = [98.3372921615202, 97.6880443388757, 97.14172604908947, 94.29928741092637, 93.50752177355503, 93.26999208234362, 5.7007125890736345, 5.225653206650831, 5.225653206650831]
  
//   hrank = [98.3372921615202, 98.32145684877277, 95.9778305621536, 92.8978622327791, 91.10847189231987, 80.58590657165479, 85.66112430720507, 71.10847189231987, 5.7007125890736345]
  
//   kmeans = [98.3372921615202, 98.36896278701505, 97.57719714964371, 96.42121931908156, 93.784639746635, 93.00079176563737, 89.59619952494062, 83.784639746635, 5.938242280285036]

var ratios = [1, 0.75, 0.5, 0.25, .2, 0.15, 0.1, 0.05, 0.01];

var dataTable = aq.table(data)
  .fold(aq.all(), { as: ['method', 'val_acc'] })
  .groupby('method')
  .params({ ratios }).derive({
    ratio: (d, $) => $.ratios[aq.default.op.row_number() - 1]
  })
  .ungroup()
  .select('method', 'val_acc', 'ratio')
  .orderby('method')
  .reify();

var dataFinal = dataTable.objects();

test = vl.markLine()
    .data(dataFinal)
    .encode(
    vl.x().fieldQ('ratio').title('Fraction of Filters Kept (per layer)').scale({"type": "log"}),
    vl.y().fieldQ('val_acc').title("Validation Accuracy (%)"),
    vl.color().fieldN('method').legend({"titleFont":"Times New Roman", "title":"Pruning Method", "titleFontSize":"16", "labelFont":"Times New Roman", "labelFontSize":"14"}),
    vl.shape().fieldN('method').legend(null),
    vl.tooltip([vl.fieldN('method'), vl.fieldQ('ratio'), vl.fieldQ('val_acc')])
    )
    .height(800)
    .width(1600)
    .render()
    .then(viewElement => {
        document.getElementById('vis').appendChild(viewElement);
    });

