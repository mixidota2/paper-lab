(() => {
  "use strict";
  const get = (name) => document.getElementById("dcdn-" + name);
  const data = JSON.parse(get("data").textContent);
  const put = (name, value) => { get(name).textContent = value; };
  const show = (value) => value === null ? "未定義（0 で割れません）" : String(Number(value.toPrecision(8)));
  const update = () => {
    const n = get("n").valueAsNumber, d = get("d").valueAsNumber;
    if (![n, d].every(value => Number.isFinite(value) && Math.abs(value) <= 1000)) {
      for (const key of ["product", "raw", "rho", "term"]) put(key, "—");
      put("note", "分子と分母には−1000以上1000以下の数を入力してください。");
      return;
    }
    const eligible = get("mask").checked;
    const rho = eligible ? Math.sign(d) / Math.max(Math.abs(d), data.epsilon) : 0;
    put("product", show(n*d));
    put("raw", d === 0 ? show(null) : Number.isFinite(n/d) ? show(n/d) : "表示範囲外");
    put("rho", show(rho));
    put("term", show(n*rho));
    put("note", !eligible ? "この分母は逆数の計算に使いません。逆数を使う項には0が入ります。"
      : d === 0 ? "この式は分母が0のとき、符号を0として逆数の項を計算します。元の比は0では割れないため未定義です。"
      : Math.abs(d) < data.epsilon ? "分母の絶対値が0.01より小さいため、逆数を求めるときは絶対値を0.01に置き換えます。"
      : "分母の絶対値が0.01以上なので、逆数を使う項は元の比と一致します。");
  };
  const compare = () => {
    const row = data.table5.rows[get("task").value];
    const mode = get("view").value;
    const [a, b] = {full:[0,1], reduced:[2,3], deployed:[0,3]}[mode];
    const val = (x) => (x/10000).toFixed(4);
    const delta = row[b] - row[a];
    put("control", val(row[a]));
    put("treatment", val(row[b]));
    put("delta", (delta > 0 ? "+" : "") + val(delta));
    put("control-label", a === 0 ? "DCNv2（比率あり）" : "DCNv2（比率なし）");
    put("treatment-label", b === 1 ? "DCDN（比率あり）" : "DCDN（比率なし）");
    put("view-note", mode === "deployed"
      ? "本番と同じ組み合わせでは、モデルを替え、入力から手作りの比率も外します。数値は保存したデータ上での評価で、A/B テストの結果ではありません。"
      : "著者は保存したデータを使い、入力をそろえたオフライン比較を行いました。");
  };
  for (const key of ["n","d","mask","task","view"]) {
    const control = get(key);
    control.addEventListener(key === "n" || key === "d" ? "input" : "change",
      ["task","view"].includes(key) ? compare : update);
    control.disabled = false;
  }
  update();
  compare();
})();
