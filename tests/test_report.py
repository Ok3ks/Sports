from src.report import LeagueWeeklyReport
import pandas as pd


class TestLeagueWeeklyReport:
    def test_init(self, league_fixture, gw_fixture):
        # TODO: test = LeagueWeeklyReport(gw_fixture, league_fixture)


    def test_weekly_score_transformation(self, league_weekly_score):
        test = LeagueWeeklyReport(1, 538731)
        test.one_df = pd.DataFrame(league_weekly_score)
        test.o_df = test.weekly_score_transformation()

        cols = test.o_df.columns
        new_cols = set(
            [
                "rank",
                "entry_id",
                "points_breakdown",
                "captain_points",
                "vice_captain_points",
            ]
        )

        assert (
            new_cols.intersection(cols) == new_cols
        ), f"Add columns {new_cols.difference(new_cols.intersection(cols))}"

    def test_merge_league_weekly_transfer(
        self, league_weekly_score, league_weekly_transfer
    ):
        test = LeagueWeeklyReport(1, 538731)
        test.one_df = pd.DataFrame(league_weekly_score)

        test.o_df = test.weekly_score_transformation()
        test.f = pd.DataFrame(league_weekly_transfer)

        test.f = test.merge_league_weekly_transfer()

        new_transfer_cols = set(
            ["transfer_points_in", "transfer_points_out", "transfers", "delta"]
        )
        cols = test.f.columns

        assert (
            new_transfer_cols.intersection(cols) == new_transfer_cols
        ), f"Add columns {new_transfer_cols.difference(new_transfer_cols.intersection(cols))}"

    def test_add_auto_sub(self, auto_sub_fixture):
        test = LeagueWeeklyReport(1, 538731)
        test.f = pd.DataFrame(auto_sub_fixture)

        test.add_auto_sub()
        auto_sub_cols = set(
            [
                "auto_sub_in_player",
                "auto_sub_out_player",
                "auto_sub_in_points",
                "auto_sub_out_points",
            ]
        )

        cols = test.f.columns
        assert (
            auto_sub_cols.intersection(cols) == auto_sub_cols
        ), f"Add columns {auto_sub_cols.difference(auto_sub_cols.intersection(cols))}"

    def test_create_report(self):
        pass

    def test_rise_and_fall(self):
        pass


if __name__ == "__main__":
    print("use pytest to run tests")
