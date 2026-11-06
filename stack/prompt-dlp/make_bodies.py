"""Write the lab's six request bodies to files, with one fake key for this run."""
import pathlib
import secrets
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "labs"))
import prompt_dlp_lab as lab  # noqa: E402

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "bodies")
out.mkdir(exist_ok=True)
key = "exk_live_" + secrets.token_hex(16)
for i, (label, host, body) in enumerate(lab.build_requests(key), 1):
    (out / f"{i}.json").write_bytes(body)
    (out / f"{i}.host").write_text(host)
    print(f"{i}.json  {host:<26} {len(body):>6} bytes  {label}")
