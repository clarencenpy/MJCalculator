import streamlit as st
import pandas as pd
import math


@st.cache(allow_output_mutation=True)
def get_data():
    return []


@st.cache(allow_output_mutation=True)
def get_cumulative():
    return []


players = [st.sidebar.text_input(f"Player{i} Name", f"Player{i}") for i in range(1, 5)]

bet = st.sidebar.number_input(
    "Winnings per 台 (cents)", step=20, min_value=20, max_value=200, value=40
)
win_type = st.sidebar.selectbox("Win Type", ("胡", "自摸", "杠", "暗杠", "花"))

winner = st.sidebar.selectbox("谁赢？", players)

if win_type == "胡":
    feeder = st.sidebar.selectbox("谁喂牌？", [p for p in players if p != winner])

if win_type == "胡" or win_type == "自摸":
    tai = st.sidebar.number_input("几台？", min_value=1, max_value=4)

if st.sidebar.button("Calculate"):
    row = {"win_type": win_type}
    if win_type == "胡":
        for player in players:
            if player == winner:
                row[player] = 4 * (bet * 2 ** (tai - 1))
            elif player == feeder:
                row[player] = -2 * (bet * 2 ** (tai - 1))
            else:
                row[player] = -1 * (bet * 2 ** (tai - 1))
    elif win_type == "自摸":
        tai += 1
        for player in players:
            if player == winner:
                row[player] = 3 * (bet * 2 ** (tai - 1))
            else:
                row[player] = -1 * (bet * 2 ** (tai - 1))
    elif win_type == "杠" or win_type == "花":
        for player in players:
            if player == winner:
                row[player] = 3 * 50
            else:
                row[player] = -1 * 50
    elif win_type == "暗杠":
        for player in players:
            if player == winner:
                row[player] = 3 * 100
            else:
                row[player] = -1 * 100
    get_data().append(row)
    get_cumulative().append(pd.DataFrame(get_data()).sum(axis=0))

st.write("# Mahjong Calculator")
if len(get_data()) > 0:
    st.write("## Game Log")
    st.write(
        pd.DataFrame(reversed(get_data())).applymap(
            lambda x: round(x / 100, 1) if not isinstance(x, str) else x
        )
    )
    st.line_chart(pd.DataFrame(get_cumulative()).drop(columns=["win_type"]))
    st.write("## O\$P\$")

    final = pd.DataFrame(get_data())
    rounds = final[final["win_type"].isin(["自摸", "胡"])]
    st.write(f"Total rounds played: {len(rounds)}")
    st.write(
        final.sum(axis=0)
        .to_frame()
        .transpose()
        .rename(index={0: "Total Winnings/Losses"})
        .applymap(lambda x: round(x / 100, 1) if not isinstance(x, str) else x)
        .drop(columns=["win_type"])
    )
    winners = {}
    losers = {}
    for player in players:
        winning = round(final[player].sum(), 1)
        if winning >= 0:
            winners[player] = winning
        else:
            losers[player] = winning

    for loser in losers:
        while losers[loser] != 0:
            for winner in winners:
                # transfer money
                amt = min(winners[winner], abs(losers[loser]))
                if amt > 0:
                    losers[loser] += amt
                    winners[winner] -= amt
                    st.write(f"{loser} pays {winner} ${amt/100}")

