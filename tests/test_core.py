import unittest
from unittest import mock

from conda_controlplane.core.conda_base import CondaContext, guess_bindir
from conda_controlplane.core.formatting import format_report_summary
from conda_controlplane.core.inspect_controlplane import inspect_all
from conda_controlplane.core.inspect_solvers import inspect_solvers


def _ctx(prefix: str = "/base") -> CondaContext:
    return CondaContext(conda_exe="/conda", base_prefix=prefix, bin_dir=f"{prefix}/bin")


def _exec_resolver(names=None):
    names = names or {"conda", "pip", "curl"}

    def _resolver(name: str):
        return f"/base/bin/{name}" if name in names else None

    return _resolver


class TestControlPlane(unittest.TestCase):
    def test_plugin_module_import_safe(self):
        # The conda plugin module must be import-safe in environments where `conda`
        # is not installed (e.g. unit test runners). Conda will import it when
        # discovering plugins via entry points.
        import conda_controlplane.plugin  # noqa: F401

    def test_guess_bindir_prefers_bin(self):
        with mock.patch("os.path.isdir", return_value=True):
            self.assertEqual(guess_bindir("/base"), "/base/bin")

    def test_inspect_solvers_selects_expected_versions(self):
        ctx = _ctx()
        pkgs = {
            "conda-libmamba-solver": "1.0.0",
            "libmamba": "2.0.0",
            "requests": "2.32.0",
            "openssl": "3.0.0",
        }
        report = inspect_solvers(ctx, pkgs, exec_resolver=_exec_resolver())
        self.assertIn("conda-libmamba-solver", report["packages"])
        self.assertEqual(report["packages"]["libmamba"], "2.0.0")
        self.assertEqual(report["executables"]["conda"], "/base/bin/conda")
        self.assertEqual(report["executables"]["pip"], "/base/bin/pip")

    def test_inspect_all_returns_all_categories(self):
        ctx = _ctx()
        pkgs = {
            "conda-libmamba-solver": "1.0.0",
            "conda-build": "24.1",
            "compilers": "1.5",
            "pip": "23.0",
            "requests": "2.31",
            "openssl": "3.0",
            "curl": "8.0",
            "auditwheel": "6.0",
        }
        payload = inspect_all(
            ctx,
            packages=[{"name": k, "version": v} for k, v in pkgs.items()],
            exec_resolver=_exec_resolver(),
        )
        cats = payload["categories"]
        self.assertEqual(set(cats.keys()), {"solvers", "compilers", "packaging", "network"})
        self.assertIn("conda-build", cats["compilers"]["packages"])
        self.assertIn("pip", cats["packaging"]["packages"])
        self.assertIn("curl", cats["network"]["executables"])

    def test_format_summary_contains_titles(self):
        ctx = _ctx()
        pkgs = {"conda-libmamba-solver": "1.0.0"}
        cat = inspect_solvers(ctx, pkgs, exec_resolver=_exec_resolver())
        payload = {"base_prefix": ctx.base_prefix, "bin_dir": ctx.bin_dir, "categories": {"solvers": cat}}
        rendered = format_report_summary(payload, verbose=True)
        self.assertIn("Solvers, Auth & Platform Detection", rendered)
        self.assertIn("Packages:", rendered)
        self.assertIn("Notes:", rendered)


if __name__ == "__main__":
    unittest.main()
