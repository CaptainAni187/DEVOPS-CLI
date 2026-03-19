"""
tests/test_devops.py
---------------------
Full test suite for the DevOps CLI.
Concepts: pytest, fixtures, tmp_path, patch, MagicMock,
          assert statements, pytest.raises
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from models.config_model  import Config, LogLevel
from core.config_loader   import load_config
from core.command_runner  import run_command
from core.log_analyzer    import analyze_logs, format_analysis, stream_log_lines
from core.system_monitor  import get_snapshot, format_snapshot
from utils.helpers        import (
    init_project_dirs, backup_file, list_backups, get_dir_size
)
from utils.env_manager    import list_env, format_env, _is_sensitive


# ══════════════════════════════════════════════════════════════════════════════
# MODELS
# ══════════════════════════════════════════════════════════════════════════════

class TestConfigModel:

    def test_config_dataclass_creates_correctly(self):
        """Config stores all fields correctly."""
        cfg = Config(
            project_name="myapp",
            log_path="logs/app.log",
            backup_dir="backups",
            monitor_interval=5,
        )
        assert cfg.project_name == "myapp"
        assert cfg.log_path == "logs/app.log"
        assert cfg.monitor_interval == 5

    def test_default_log_level_is_info(self):
        """Log level defaults to INFO when not specified."""
        cfg = Config("app", "logs/app.log", "backups", 5)
        assert cfg.log_level == LogLevel.INFO

    def test_string_log_level_converts_to_enum(self):
        """Passing a string log level is converted to enum in __post_init__."""
        cfg = Config("app", "logs/app.log", "backups", 5, log_level="ERROR")
        assert cfg.log_level == LogLevel.ERROR

    def test_log_level_enum_values(self):
        """All four log levels exist with correct string values."""
        assert LogLevel.DEBUG.value   == "DEBUG"
        assert LogLevel.INFO.value    == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value   == "ERROR"

    def test_invalid_log_level_raises(self):
        """An invalid log level string raises ValueError."""
        with pytest.raises(ValueError):
            Config("app", "logs/app.log", "backups", 5, log_level="INVALID")


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG LOADER
# ══════════════════════════════════════════════════════════════════════════════

class TestConfigLoader:

    def test_loads_valid_yaml(self, sample_config_file):
        """Valid config.yaml produces a correct Config dataclass."""
        # __wrapped__ bypasses lru_cache so we can use a custom path
        cfg = load_config.__wrapped__(sample_config_file)
        assert cfg.project_name == "testapp"
        assert cfg.monitor_interval == 3
        assert cfg.log_level == LogLevel.INFO

    def test_missing_file_raises_file_not_found(self):
        """Non-existent config path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config.__wrapped__("/no/such/file.yaml")

    def test_empty_file_raises_value_error(self, tmp_path):
        """Empty config file raises ValueError."""
        empty = tmp_path / "empty.yaml"
        empty.write_text("")
        with pytest.raises(ValueError):
            load_config.__wrapped__(str(empty))

    def test_missing_keys_raises_key_error(self, tmp_path):
        """Config missing required keys raises KeyError."""
        bad = tmp_path / "bad.yaml"
        bad.write_text("project_name: only_this\n")
        with pytest.raises(KeyError):
            load_config.__wrapped__(str(bad))

    def test_cache_returns_same_object(self):
        """lru_cache returns identical object on repeated calls."""
        # Call twice with the real config path
        cfg1 = load_config()
        cfg2 = load_config()
        assert cfg1 is cfg2   # same object — not just equal, literally the same

    def test_cache_has_one_miss_after_first_call(self):
        """Cache miss count stays at 1 after multiple calls."""
        load_config()
        load_config()
        info = load_config.cache_info()
        assert info.misses == 1
        assert info.hits >= 1


# ══════════════════════════════════════════════════════════════════════════════
# COMMAND RUNNER
# ══════════════════════════════════════════════════════════════════════════════

class TestCommandRunner:

    def test_successful_command_returns_success_true(self):
        """echo command succeeds and captures output."""
        result = run_command(["echo", "hello"])
        assert result["success"] is True
        assert "hello" in result["stdout"]
        assert result["returncode"] == 0

    def test_failed_command_returns_success_false(self):
        """Command that fails returns success=False with non-zero code."""
        result = run_command(["ls", "/path/that/does/not/exist"])
        assert result["success"] is False
        assert result["returncode"] != 0

    def test_nonexistent_command_returns_success_false(self):
        """Command that doesn't exist returns success=False cleanly."""
        result = run_command(["totally_fake_command_xyz"])
        assert result["success"] is False
        assert "not found" in result["stderr"].lower()
        assert result["returncode"] == -1

    def test_timeout_returns_success_false(self):
        """Command that exceeds timeout is killed and returns False."""
        result = run_command(["sleep", "10"], timeout=1)
        assert result["success"] is False
        assert "timed out" in result["stderr"].lower()

    def test_result_dict_has_required_keys(self):
        """Result dict always contains all four expected keys."""
        result = run_command(["echo", "test"])
        assert "success"    in result
        assert "stdout"     in result
        assert "stderr"     in result
        assert "returncode" in result

    def test_subprocess_called_with_correct_args(self):
        """subprocess.run is called with the exact parameters we expect."""
        with patch("core.command_runner.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="ok",
                stderr=""
            )
            run_command(["pytest", "--verbose"])
            mock_run.assert_called_once_with(
                ["pytest", "--verbose"],
                capture_output=True,
                text=True,
                cwd=None,
                timeout=120,
            )


# ══════════════════════════════════════════════════════════════════════════════
# LOG ANALYZER
# ══════════════════════════════════════════════════════════════════════════════

class TestLogAnalyzer:

    def test_counts_all_levels_correctly(self, sample_log_file):
        """Correct count for each log level in sample file."""
        result = analyze_logs(sample_log_file)
        assert result["counts"]["INFO"]    == 4
        assert result["counts"]["ERROR"]   == 2
        assert result["counts"]["WARNING"] == 2
        assert result["counts"]["DEBUG"]   == 1

    def test_total_lines_matches_file(self, sample_log_file):
        """total_lines matches actual number of lines in file."""
        result = analyze_logs(sample_log_file)
        assert result["total_lines"] == 9

    def test_error_lines_captured(self, sample_log_file):
        """errors list contains only ERROR lines."""
        result = analyze_logs(sample_log_file)
        assert len(result["errors"]) == 2
        # Every line in errors must contain ERROR
        assert all("ERROR" in line for line in result["errors"])

    def test_empty_file_returns_zero_counts(self, empty_log_file):
        """Empty log file produces all-zero counts."""
        result = analyze_logs(empty_log_file)
        assert result["total_lines"] == 0
        assert result["counts"]["ERROR"] == 0
        assert result["errors"] == []

    def test_missing_log_file_returns_empty(self):
        """Non-existent log file returns empty result gracefully."""
        result = analyze_logs("/no/such/file.log")
        assert result["total_lines"] == 0

    def test_generator_yields_strings(self, sample_log_file):
        """stream_log_lines generator yields string lines."""
        gen = stream_log_lines(sample_log_file)
        first_line = next(gen)
        assert isinstance(first_line, str)
        assert len(first_line) > 0

    def test_generator_yields_correct_count(self, sample_log_file):
        """Generator yields exactly as many lines as the file contains."""
        lines = list(stream_log_lines(sample_log_file))
        assert len(lines) == 9

    def test_format_analysis_contains_all_levels(self, sample_log_file):
        """Formatted output string contains all level labels."""
        result  = analyze_logs(sample_log_file)
        output  = format_analysis(result)
        assert "ERROR"   in output
        assert "WARNING" in output
        assert "INFO"    in output
        assert "DEBUG"   in output

    def test_format_analysis_shows_recent_errors(self, sample_log_file):
        """Formatted output includes Recent Errors section when errors exist."""
        result = analyze_logs(sample_log_file)
        output = format_analysis(result)
        assert "Recent Errors" in output


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM MONITOR
# ══════════════════════════════════════════════════════════════════════════════

class TestSystemMonitor:

    def test_snapshot_contains_all_keys(self):
        """Snapshot dict has all five expected keys."""
        snap = get_snapshot()
        for key in ("timestamp", "cpu", "ram", "disk", "processes"):
            assert key in snap

    def test_cpu_is_valid_percentage(self):
        """CPU value is between 0 and 100."""
        snap = get_snapshot()
        assert 0 <= snap["cpu"] <= 100

    def test_ram_is_valid_percentage(self):
        """RAM value is between 0 and 100."""
        snap = get_snapshot()
        assert 0 <= snap["ram"] <= 100

    def test_process_count_is_positive(self):
        """Process count is a positive integer."""
        snap = get_snapshot()
        assert snap["processes"] > 0
        assert isinstance(snap["processes"], int)

    def test_snapshot_uses_mocked_psutil(self):
        """With mocked psutil, snapshot returns exactly the mocked values."""
        with patch("core.system_monitor.psutil") as mock_psutil:
            mock_psutil.cpu_percent.return_value         = 42.0
            mock_psutil.virtual_memory.return_value.percent = 60.0
            mock_psutil.disk_usage.return_value.percent  = 55.0
            mock_psutil.pids.return_value                = list(range(200))

            snap = get_snapshot()

            assert snap["cpu"]       == 42.0
            assert snap["ram"]       == 60.0
            assert snap["disk"]      == 55.0
            assert snap["processes"] == 200

    def test_format_snapshot_contains_all_fields(self):
        """Formatted snapshot string contains all display labels."""
        snap   = get_snapshot()
        output = format_snapshot(snap)
        for label in ("CPU", "RAM", "Disk", "Time", "Processes"):
            assert label in output


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

class TestHelpers:

    def test_init_creates_all_directories(self, tmp_path):
        """init_project_dirs creates all four standard folders."""
        created = init_project_dirs(str(tmp_path))
        for folder_name in ["logs", "backups", "temp", "data"]:
            assert (tmp_path / folder_name).exists()
        assert len(created) == 4

    def test_init_is_idempotent(self, tmp_path):
        """Calling init_project_dirs twice does not raise an error."""
        init_project_dirs(str(tmp_path))
        init_project_dirs(str(tmp_path))   # second call — should not crash

    def test_backup_creates_file(self, tmp_path):
        """backup_file creates a new file in the backup directory."""
        src = tmp_path / "config.yaml"
        src.write_text("project_name: test")

        dest = backup_file(str(src), str(tmp_path))

        assert Path(dest).exists()

    def test_backup_filename_contains_timestamp(self, tmp_path):
        """Backup filename includes the original stem and a timestamp."""
        src = tmp_path / "config.yaml"
        src.write_text("project_name: test")

        dest = backup_file(str(src), str(tmp_path))

        assert "config_" in Path(dest).name
        assert Path(dest).suffix == ".yaml"

    def test_backup_preserves_content(self, tmp_path):
        """Backed up file has identical content to source."""
        content = "project_name: test\nlog_level: INFO\n"
        src = tmp_path / "config.yaml"
        src.write_text(content)

        dest = backup_file(str(src), str(tmp_path))

        assert Path(dest).read_text() == content

    def test_backup_missing_file_raises(self, tmp_path):
        """Backing up a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            backup_file(str(tmp_path / "missing.yaml"), str(tmp_path))

    def test_list_backups_returns_sorted_list(self, tmp_path):
        """list_backups returns a sorted list of file paths."""
        (tmp_path / "a.log").write_text("a")
        (tmp_path / "b.log").write_text("b")
        (tmp_path / "c.log").write_text("c")

        result = list_backups(str(tmp_path))

        assert len(result) == 3
        assert result == sorted(result)

    def test_list_backups_empty_dir_returns_empty_list(self, tmp_path):
        """Empty backup directory returns empty list without error."""
        result = list_backups(str(tmp_path))
        assert result == []

    def test_list_backups_missing_dir_returns_empty_list(self):
        """Non-existent backup directory returns empty list without error."""
        result = list_backups("/no/such/directory")
        assert result == []

    def test_get_dir_size_returns_string(self, tmp_path):
        """get_dir_size returns a non-empty string."""
        (tmp_path / "file.txt").write_text("hello world")
        size = get_dir_size(str(tmp_path))
        assert isinstance(size, str)
        assert len(size) > 0


# ══════════════════════════════════════════════════════════════════════════════
# ENV MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class TestEnvManager:

    def test_sensitive_key_detection_true(self):
        """Keys containing sensitive words are flagged correctly."""
        assert _is_sensitive("API_KEY")      is True
        assert _is_sensitive("DB_PASSWORD")  is True
        assert _is_sensitive("AUTH_TOKEN")   is True
        assert _is_sensitive("DATABASE_URL") is True

    def test_sensitive_key_detection_false(self):
        """Non-sensitive keys are not flagged."""
        assert _is_sensitive("ENVIRONMENT") is False
        assert _is_sensitive("DEBUG")       is False
        assert _is_sensitive("APP_NAME")    is False

    def test_list_env_redacts_sensitive_values(self, tmp_path):
        """Sensitive values are replaced with **** in list_env output."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "API_KEY=super_secret\n"
            "ENVIRONMENT=development\n"
            "DB_PASSWORD=hunter2\n"
        )
        result = list_env(str(env_file))
        assert result["API_KEY"]     == "****"
        assert result["DB_PASSWORD"] == "****"
        assert result["ENVIRONMENT"] == "development"  # not redacted

    def test_list_env_returns_all_keys(self, tmp_path):
        """list_env returns all keys from the .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("A=1\nB=2\nC=3\n")
        result = list_env(str(env_file))
        assert set(result.keys()) == {"A", "B", "C"}

    def test_format_env_contains_key_names(self, tmp_path):
        """format_env output string contains key names."""
        env_file = tmp_path / ".env"
        env_file.write_text("ENVIRONMENT=production\nDEBUG=false\n")
        output = format_env(str(env_file))
        assert "ENVIRONMENT" in output
        assert "DEBUG"       in output

    def test_format_env_empty_file_returns_message(self, tmp_path):
        """Empty .env file returns a friendly message."""
        env_file = tmp_path / ".env"
        env_file.write_text("")
        output = format_env(str(env_file))
        assert "No environment variables" in output