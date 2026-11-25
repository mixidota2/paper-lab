'use strict';
const get=id=>document.getElementById(id);
const messages={
  increment:'この例では、値引き品を買った人は通常価格なら買いません。値引き品が売れた数だけ、その商品の総販売数が増えます。',
  selection:'この例では、値引きしなくても同じ数が売れます。回帰の傾きは最初の例と同じ1ですが、値引きで増えた販売数は0個です。',
  substitution:'この例では、値引き品を買った人は、値引きがなければ同じ商品を通常価格で買います。その商品の総販売数は変わりません。'
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
