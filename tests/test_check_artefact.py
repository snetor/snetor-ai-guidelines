"""check_artefact.py: an artifact built to the contract passes, one built on a laptop does not.

The deploy skill used to discover, at deployment, what a business artifact carried: addresses,
browser storage, a home-made login. A v2 brought it all back. This check moves that audit to the
moment the artifact is built, and is the gate the developer runs again before the image build.
"""
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "plugins/snetor-skills/skills/snetor-app-artefact"
sys.path.insert(0, str(SKILL / "scripts"))

from check_artefact import STORE, check  # noqa: E402

ADAPTER = STORE.read_text(encoding="utf-8")


def page(body, adapter=ADAPTER):
    return f"<!doctype html><html><body><script>\n{adapter}\n{body}\n</script></body></html>"


def failures(html, fiche=None, deploy=False):
    return [axis for axis, ok, _ in check(html, fiche, deploy) if not ok]


def test_a_page_built_to_the_contract_passes():
    html = page('const s = await snetorStore.load("stock-mensuel"); await snetorStore.save("stock-mensuel", s.valeur, s.version);')
    assert failures(html) == []


def test_a_laptop_artifact_fails_on_every_axis():
    html = page("""
      localStorage.setItem("x", 1);  // persistence outside the adapter
      const owner = "jane.doe@example.com", tel = "+33 6 12 34 56 78";
      document.body.innerHTML = '<input type="password">';
      crypto.subtle.digest("SHA-256", data);
      fetch("https://api.example.com/push", {method: "POST"});
      const copy = new Blob([document.documentElement.outerHTML]);
    """, adapter="")
    assert failures(html) == ["personal data", "persistence", "authentication", "external calls", "distribution"]


def test_the_adapter_is_the_only_place_browser_storage_may_appear():
    tampered = ADAPTER.replace("const memory = {};", "const memory = {}; sessionStorage.clear();")
    assert failures(page("", tampered)) == []                 # inside the block: allowed
    assert failures(page("sessionStorage.clear();")) == ["persistence"]


def test_exceptions_are_counted_exactly():
    fiche = {"exceptions": [{"text": "owner@snetor.com", "count": 1, "decided_by": "owner", "date": "2026-10-01"}]}
    assert failures(page('const c = "owner@snetor.com";'), fiche) == []
    drift = page('const c = "owner@snetor.com"; const to = ["owner@snetor.com"];')
    assert failures(drift, fiche) == ["personal data"]       # it came back out somewhere else


def test_codes_amounts_and_image_names_are_not_personal_data():
    assert failures(page('const sap = "0612345678", img = "logo@2x.png", tel = "06 12 34 56 78";')) == ["personal data"]
    assert failures(page('const sap = "0612345678", img = "logo@2x.png";')) == []


def test_state_keys_must_be_what_the_server_accepts():
    assert failures(page('snetorStore.load("Stock Mensuel");')) == ["state keys"]


def test_deploy_mode_requires_the_server_switch():
    html = page("")
    assert failures(html, deploy=True) == ["mode"]
    assert failures(html.replace('SNETOR_MODE = "demo"', 'SNETOR_MODE = "server"'), deploy=True) == []


def test_cli_exit_code(tmp_path, capsys):
    from check_artefact import main
    good, bad = tmp_path / "good.html", tmp_path / "bad.html"
    good.write_text(page(""), encoding="utf-8")
    bad.write_text(page("localStorage.x = 1"), encoding="utf-8")
    fiche = tmp_path / "app.json"
    fiche.write_text(json.dumps({"exceptions": []}), encoding="utf-8")
    assert main([str(good), "--fiche", str(fiche)]) == 0
    assert main([str(bad)]) == 1
    assert "FAIL  persistence" in capsys.readouterr().out


RUN_STORE = r"""
const assert = require("assert");
const src = require("fs").readFileSync(process.argv[2], "utf8");
const make = (mode, fetch) => new Function("fetch", src.replace('SNETOR_MODE = "demo"', `SNETOR_MODE = "${mode}"`)
  + "\nreturn snetorStore;")(fetch);
const reply = (status, body) => ({ status, json: async () => body });
(async () => {
  // demo: no localStorage under Node, so the in-memory fallback carries the versions
  const demo = make("demo");
  assert.deepStrictEqual(await demo.load("k"), { valeur: null, version: 0 });
  assert.deepStrictEqual(await demo.save("k", 1, 0), { ok: true, version: 1 });
  assert.strictEqual((await demo.save("k", 2, 0)).ok, false);           // stale version: conflict
  assert.strictEqual((await demo.me()).grade, "admin");
  // server: the three outcomes of a write, as the platform answers them
  const calls = [];
  const server = make("server", async (url, init) => {
    calls.push([url, init && init.method]);
    if (url === "/api/moi") return reply(200, { utilisateur: "u", nom: "U", grade: "reader" });
    if (!init) return reply(200, { valeur: 5, version: 3 });
    const { version } = JSON.parse(init.body);
    if (version === 3) return reply(200, { version: 4 });
    if (version === 2) return reply(409, { valeur: 9, version: 3, maj_par: "someone" });
    return reply(403, { erreur: "lecture seule", detail: "ask for the writer group" });
  });
  assert.strictEqual((await server.me()).grade, "reader");
  assert.deepStrictEqual(await server.load("k"), { valeur: 5, version: 3 });
  assert.deepStrictEqual(await server.save("k", 6, 3), { ok: true, version: 4 });
  assert.strictEqual((await server.save("k", 6, 2)).conflict.maj_par, "someone");
  assert.strictEqual((await server.save("k", 6, 1)).forbidden, "ask for the writer group");
  assert.deepStrictEqual(calls[2], ["/api/etat/k", "PUT"]);
  console.log("store ok");
})().catch(e => { console.error(e); process.exit(1); });
"""


def test_the_store_runs_in_both_modes(tmp_path):
    import shutil
    import subprocess
    import pytest
    if not shutil.which("node"):
        pytest.skip("node not installed")
    script = tmp_path / "run_store.js"
    script.write_text(RUN_STORE, encoding="utf-8")
    r = subprocess.run(["node", str(script), str(STORE)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
