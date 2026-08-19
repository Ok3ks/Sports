from src.report import League


class TestLeague:
    def test_init(self, classic_league):
        test = League(classic_league)
        assert test.league_id == 87552
        assert test.participants == []
        assert test.PAGE_COUNT == 1

    async def test_obtain_league_participants(
        self, classic_league, league_fill_fixture
    ):
        test = League(classic_league)
        test.participants = league_fill_fixture

        obj = await test.obtain_league_participants()
        keys = set(
            [
                "entry",
                "entry_name",
                "id",
                "event_total",
                "player_name",
                "rank",
                "last_rank",
                "rank_sort",
                "total",
            ]
        )

        diff = keys.difference(test.participants[0].keys())
        assert keys.intersection(test.participants[0].keys()) == keys, (
            f"Vital keys missing, Add keys -  {diff}"
        )

        assert len(test.participants) == len(obj)
        assert type(test.participants) is list

        assert test.entry_ids is not None
        assert type(test.entry_ids) is list

    def test_get_league_count(self, classic_league, league_fill_fixture):
        test = League(classic_league)
        test.participants = league_fill_fixture

        assert test.get_league_count() == len(league_fill_fixture)

    async def test_league_get_participant_name(self, classic_league, league_fill_fixture):
        test = League(classic_league)
        test.participants = league_fill_fixture
        await test.get_participant_name()

        assert "entry" in test.participants[0].keys()
        assert "entry_name" in test.participants[0].keys()

        assert type(list(test.participant_name.values())[0]) is str

    async def test_league_get_gw_transfers(
        self, classic_league, league_weekly_transfer, gw_fixture, mocker
    ):
        test = League(classic_league)
        mocker.patch.object(
            test, "get_gw_transfers", return_value=league_weekly_transfer
        )

        spy = mocker.spy(test, "get_gw_transfers")
        await test.get_gw_transfers(gw_fixture)

        assert spy.call_count == 1
        assert spy.spy_return == league_weekly_transfer
