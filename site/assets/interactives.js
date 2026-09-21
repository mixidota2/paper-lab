/* Progressive enhancement. All teaching data is embedded: no network or dependencies. */
(() => {
  'use strict';
  const palette = ['#086b5e', '#a14d26', '#536893'];
  const number = value => Number(value).toLocaleString('ja-JP', {maximumFractionDigits: 4});
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function button(text, action) {
    const node = el('button', '', text);
    node.type = 'button';
    node.addEventListener('click', action);
    return node;
  }
  function svgNode(tag, attrs, text) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function flow(root, config) {
    let step = 0;
    let mode = 'proposed';
    const controls = el('div', 'interactive-controls');
    controls.setAttribute('role', 'group');
    controls.setAttribute('aria-label', '比較する設計');
    const baseline = button('比較側の設計', () => {mode = 'baseline'; render();});
    const proposed = button('論文の設計', () => {mode = 'proposed'; render();});
    controls.append(baseline, proposed);
    const path = el('div', 'flow-path');
    path.setAttribute('aria-label', '処理段階を選択');
    const detail = el('div', 'flow-detail');
    detail.setAttribute('aria-live', 'polite');
    detail.setAttribute('aria-atomic', 'true');
    const heading = el('h3');
    const comparison = el('p');
    const explanation = el('p');
    detail.append(heading, comparison, explanation);
    const nodes = config.stages.map((stage, i) => {
      const node = button('', () => {step = i; render();});
      node.className = 'flow-node';
      node.append(el('span', 'step-number', String(i+1).padStart(2, '0')),
                  el('span', 'node-title', stage.title), el('strong'));
      path.append(node);
      return node;
    });
    const footer = el('div', 'step-footer');
    const previous = button('← 前へ', () => {step = Math.max(0, step-1); render();});
    const next = button('次へ →', () => {step = Math.min(nodes.length-1, step+1); render();});
    const progress = el('span');
    footer.append(previous, progress, next);
    root.append(controls, path, detail, footer);
    function render() {
      baseline.setAttribute('aria-pressed', mode === 'baseline');
      proposed.setAttribute('aria-pressed', mode === 'proposed');
      nodes.forEach((node, i) => {
        node.setAttribute('aria-current', i === step ? 'step' : 'false');
        node.querySelector('strong').textContent = config.stages[i][mode];
      });
      const stage = config.stages[step];
      heading.textContent = `${step+1}. ${stage.title}`;
      comparison.textContent = `${mode === 'baseline' ? '比較側' : '論文の設計'}：${stage[mode]}`;
      explanation.textContent = stage.detail;
      progress.textContent = `${step+1} / ${nodes.length}`;
      previous.disabled = step === 0;
      next.disabled = step === nodes.length-1;
    }
    render();
  }
  function explorer(root, data, id) {
    let index = data.default;
    let localScale = false;
    const label = el('label', 'slider-label', data.label);
    label.htmlFor = `${id}-range`;
    const value = el('output');
    value.htmlFor = `${id}-range`;
    label.append(value);
    const range = el('input');
    range.id = `${id}-range`;
    range.type = 'range'; range.min = '0'; range.max = String(data.frames.length-1); range.step = '1'; range.value = String(index);
    const controls = el('div', 'interactive-controls');
    const previous = button('− ひとつ前', () => select(index-1));
    const next = button('＋ ひとつ先', () => select(index+1));
    const reset = button('初期条件に戻す', () => select(data.default));
    const scale = button('棒の尺度：全条件で固定', () => {
      localScale = !localScale;
      scale.textContent = localScale ? '棒の尺度：現在の条件' : '棒の尺度：全条件で固定';
      scale.setAttribute('aria-pressed', localScale);
      render();
    });
    scale.setAttribute('aria-pressed', 'false');
    controls.append(previous, next, reset, scale);
    const metric = el('p', 'chart-metric', data.metric + ' · 棒の起点は0');
    const chart = el('div', 'bar-chart');
    const note = el('p', 'explorer-note');
    note.setAttribute('aria-live', 'polite'); note.setAttribute('aria-atomic', 'true');
    const traces = el('div');
    const details = el('details');
    details.append(el('summary', '', '現在の条件の数値を表で読む'));
    const tableMount = el('div', 'chart-data');
    tableMount.tabIndex = 0; tableMount.setAttribute('role', 'region'); tableMount.setAttribute('aria-label', '実験データの表');
    details.append(tableMount);
    root.append(label, range, controls, metric, chart, note, traces, details);
    const maximum = Math.max(1e-9, ...data.frames.flatMap(f => f.bars.map(b => b.value)));
    range.addEventListener('input', () => select(Number(range.value)));
    function select(nextIndex) {
      index = Math.max(0, Math.min(data.frames.length-1, nextIndex));
      render();
    }
    function render() {
      const f = data.frames[index];
      range.value = String(index);
      range.setAttribute('aria-valuetext', `${f.value}${data.unit}`);
      value.value = `${number(f.value)}${data.unit}`;
      previous.disabled = index === 0;
      next.disabled = index === data.frames.length-1;
      chart.replaceChildren();
      const max = localScale ? Math.max(1e-9, ...f.bars.map(b => b.value)) : maximum;
      f.bars.forEach(b => {
        const row = el('div', 'bar-row');
        const label = el('div', 'bar-label');
        label.append(el('span', '', b.label), el('strong', '', number(b.value)));
        const track = el('div', 'bar-track');
        track.setAttribute('aria-hidden', 'true');
        const fill = el('div', 'bar-fill'); fill.style.width = `${100*b.value/max}%`;
        track.append(fill); row.append(label, track); chart.append(row);
      });
      note.textContent = f.note;
      traces.replaceChildren(); tableMount.replaceChildren();
      const table = el('table');
      const caption = el('caption', 'sr-only', `条件 ${f.value}：${data.metric}`);
      const head = el('thead'); const hr = el('tr');
      ['指標', '値'].forEach(t => {const th=el('th','',t);th.scope='col';hr.append(th);});
      head.append(hr); const body=el('tbody');
      f.bars.forEach(b => {const tr=el('tr');const th=el('th','',b.label);th.scope='row';tr.append(th,el('td','',number(b.value)));body.append(tr);});
      table.append(caption,head,body);tableMount.append(table);
      if (f.lines && f.lines.length) {
        drawLines(traces, f.lines, `${id}-plot`);
        const traceTable = el('table');
        const header=el('thead'); const row=el('tr');
        ['点',...f.lines.map(l=>l.label)].forEach(t=>{const th=el('th','',t);th.scope='col';row.append(th);});
        header.append(row);traceTable.append(header);const rows=el('tbody');
        const n=Math.max(...f.lines.map(l=>l.values.length));
        for(let i=0;i<n;i++) {const row=el('tr');const th=el('th','',i+1);th.scope='row';row.append(th);f.lines.forEach(l=>row.append(el('td','',l.values[i] === undefined ? '—' : number(l.values[i]))));rows.append(row);}
        traceTable.append(rows);tableMount.append(traceTable);
      }
    }
    render();
  }
  function drawLines(mount, lines, id) {
    const all = lines.flatMap(l => l.values);
    const lo = Math.min(0, ...all), hi = Math.max(1e-9, ...all);
    const n = Math.max(...lines.map(l=>l.values.length));
    const x = i => 48+440*i/Math.max(1,n-1);
    const y = value => 204-176*(value-lo)/(hi-lo || 1);
    const svg = svgNode('svg', {viewBox:'0 0 520 240',role:'img','aria-labelledby':`${id}-title`,'aria-describedby':`${id}-desc`});
    svg.classList.add('chart-svg');
    svg.append(svgNode('title',{id:`${id}-title`},'現在の条件の系列と計算値'),svgNode('desc',{id:`${id}-desc`},'色と線種で系列を区別。点の番号は1から始まります。正確な値は下のデータ表で読めます。'));
    for (let i=0;i<=4;i++) {
      const v=lo+(hi-lo)*i/4;
      svg.append(svgNode('line',{x1:48,x2:488,y1:y(v),y2:y(v),stroke:'#dce2d8','stroke-width':1}));
      svg.append(svgNode('text',{x:40,y:y(v)+4,'text-anchor':'end'},Number(v.toFixed(1))));
    }
    svg.append(svgNode('text',{x:48,y:228},'1'),svgNode('text',{x:488,y:228,'text-anchor':'end'},String(n)));
    const legend=el('div','chart-legend');
    lines.forEach((line,i)=>{
      svg.append(svgNode('polyline',{points:line.values.map((v,j)=>`${x(j)},${y(v)}`).join(' '),fill:'none',stroke:palette[i%3],'stroke-width':3,'stroke-dasharray':['none','8 5','2 5'][i%3],'stroke-linejoin':'round'}));
      if(line.values.length === 1) svg.append(svgNode('circle',{cx:x(0),cy:y(line.values[0]),r:4,fill:palette[i%3]}));
      const item=el('span','',line.label);item.style.setProperty('--series-color',palette[i%3]);legend.append(item);
    });
    mount.append(svg,legend,el('p','trace-caption','横軸：系列内の点番号。縦軸：各系列の値（現在の条件に合わせて尺度が変わります）。単位と点の意味は実験の説明を参照。'));
  }
  document.querySelectorAll('[data-interactive]').forEach((section, i) => {
    const mount = section.querySelector('[data-mount]');
    try {
      const config = JSON.parse(section.querySelector('[data-config]').textContent);
      if (config.kind === 'flow') flow(mount, config);
      else explorer(mount, JSON.parse(section.querySelector('[data-results]').textContent), `experiment-${i}`);
      section.querySelector('[data-fallback]').hidden = true;
      section.dataset.ready = 'true';
    } catch (error) {
      // A malformed figure does not remove the readable server-rendered fallback.
      mount.replaceChildren();
      console.error('Interactive figure could not initialize', error);
    }
  });
})();

// Paper-specific probes use saved Python results; no performance values are simulated in the UI.
document.querySelectorAll('[data-paper-probe]').forEach(root => {
  const data = JSON.parse(root.querySelector('[data-probe-data]').textContent);
  const output = root.querySelector('[data-probe-output]');
  const paragraph = text => { const p = document.createElement('p'); p.textContent = text; return p; };
  const update = () => {
    output.replaceChildren();
    if (root.dataset.paperProbe === 'univa-commercial-sid-gar') {
      const alpha = Number(root.querySelector('[data-alpha]').value);
      const width = Number(root.querySelector('[data-beam]').value);
      const masked = root.querySelector('[data-mask]').checked;
      const f = data.frames.find(f => f.alpha === alpha && f.width === width && f.personalized === masked);
      output.append(paragraph(`α=${alpha} / beam=${width} / ${masked ? 'personalized trie' : 'global → 事後filter'}：有効経路 ${f.valid_count} 件`));
      const paths = document.createElement('div'); paths.className = 'candidate-paths';
      f.candidates.forEach(c => {const el = document.createElement('div'); el.className = `candidate-path ${c.valid ? 'valid' : 'invalid'}`; el.textContent = `${c.path} ｜ log score ${c.score.toFixed(3)} ｜ ${c.valid ? '配信可' : '事後除外'}`; paths.append(el);});
      output.append(paths);
    } else if (root.dataset.paperProbe === 'cq-sid-eg-grpo-tmall') {
      const width = Number(root.querySelector('[data-cluster-beam]').value);
      const f = data.frames.find(f => f.beam === width);
      output.append(paragraph(`一意IDなら${f.unique_items}商品。クラスタなら${f.cluster_items}商品 → top-20後 ${f.after_cap}商品。`));
      const chips = document.createElement('div'); chips.className = 'item-chips';
      f.selected.forEach(n => {const chip = document.createElement('span'); chip.textContent = n; if (n===23) chip.className='target'; chips.append(chip);});
      output.append(chips, paragraph(`target=23：${f.target_retained ? '残る' : '落ちる'}。候補の追加が切り詰め後の保持を保証するわけではない。`));
      const k = root.querySelector('[data-expert]').value;
      const values = data.group_examples[k];
      root.querySelector('[data-expert-output]').textContent = `K=${k}：生成8件のadvantage ${values[0].toFixed(3)}${Number(k) ? ` / expert ${k}件のadvantage ${values[8].toFixed(3)}` : ' / 報酬差がなく、更新信号はゼロ'}`;
    } else {
      const p = Number(root.querySelector('[data-failure]').value);
      const f = data.frames[p];
      root.querySelector('[data-p-value]').textContent = `${p}%`;
      root.querySelector('[data-p-marker]').style.left = `${p}%`;
      output.append(paragraph(`100タスク当たり 回復 ${f.recovered_per_100.toFixed(2)} − 破壊 ${f.disrupted_per_100.toFixed(2)} = ${f.delta_pp > 0 ? '+' : ''}${f.delta_pp.toFixed(2)}ポイント`));
      output.append(paragraph(f.delta_pp > 0 ? '仮定した率では改善側。ただしpilotの不確かさと安全余裕を別に調べる。' : f.delta_pp < 0 ? '仮定した率では悪化側。常時介入を見送る条件。' : '期待差はゼロ。'));
      if (p === 0 || p === 100) output.append(paragraph('端点：このtask群だけからはrかdを推定できない。表示は外部から率を固定した感度分析。'));
    }
  };
  root.querySelectorAll('select,input').forEach(el => el.addEventListener('input',update));
  update();
});

// Two distinct controls: reading published SLO points and a synthetic GFSA gate.
document.querySelectorAll('[data-b17]').forEach(panel => {
  const data = JSON.parse(panel.querySelector('[data-values]').textContent);
  const control = panel.querySelector('[data-control]');
  const output = panel.querySelector('[data-output]');
  const update = () => {
    if (panel.dataset.b17 === 'slo') {
      const limit = Number(control.value);
      const feasible = data.filter(row => row[3] <= limit);
      const row = feasible.at(-1);
      output.textContent = row ? `p99上限${limit}ms：表の条件を満たす最大BWは${row[0]}。GPU p99=${row[3]}ms、平均=${row[2]}ms、P@100=${row[4]}。著者の実測点から選択。` : '表の実測点に条件を満たすものはない。';
    } else {
      const row = data[Number(control.value)];
      output.textContent = `w=${row.weight}：共有attention [${row.shared_attention.map(x=>x.toFixed(3)).join(', ')}]。SID側pool [${row.sid_pooled.map(x=>x.toFixed(3)).join(', ')}]、ID側pool [${row.item_pooled.map(x=>x.toFixed(3)).join(', ')}]。対照整列の寄与=${row.weighted_alignment_loss.toFixed(4)}。人工例。`;
    }
  };
  control.addEventListener('input', update);
  control.addEventListener('change', update);
  update();
});

// September 18: render precomputed Python experiment frames, without recomputing results.
document.querySelectorAll('[data-b18]').forEach(root => {
  const frames = JSON.parse(root.querySelector('[data-frames]').textContent);
  const select = root.querySelector('select');
  const output = root.querySelector('[data-output]');
  const update = () => { output.innerHTML = frames[Number(select.value)]; };
  select.addEventListener('change', update);
  update();
});

// Paper-specific September 21 displays use precomputed experiment traces.
document.querySelectorAll('[data-b21]').forEach(root => {
  const frames = JSON.parse(root.querySelector('[data-frames]').textContent);
  const select = root.querySelector('select');
  const output = root.querySelector('[data-output]');
  const update = () => { output.innerHTML = frames[Number(select.value)]; };
  select.addEventListener('change', update);
  update();
});
