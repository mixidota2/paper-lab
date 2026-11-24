'use strict';
const get=id=>document.getElementById(id);
const messages={
  increment:'値引き品を買った人は、値引きがなければ買いません。値引き販売の分だけ総販売数が増えます。',
  selection:'売れ行きのよい日は、値引きしなかった場合も同じ数が売れます。傾きは最初の例と同じですが、値引きで増えた数はゼロです。',
  substitution:'値引き品を買った人は、値引きがなければ通常価格で買います。買った商品の個数は変わりません。'
};
function render(){
  const mode=get('mode').value;
  const current=MarkdownToy.evaluate(mode);
  for(const id of ['slope','total_slope','regular_slope','mean_residual','true_increment']) get(id).textContent=String(current[id]);
  get('out').textContent=messages[mode];
  get('counts').textContent='値引き品が売れなかった行は'+current.base_rows+'件です。そのうち、値引きシールを貼っても売れなかった行が'+current.sticker_only_rows+'件あります。値引き品が売れた行は'+current.positive_ds_rows+'件です。';
}
get('mode').addEventListener('change',render);
get('reset').addEventListener('click',()=>{get('mode').value='increment';render();});
render();
