from brownie import network, exceptions
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
    INITIAL_VALUE,
)
import pytest
from scripts.deploy import deploy_token_farm_and_dapp_token


def test_set_price_feed_contract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    price_feed_address = get_contract("eth_usd_price_feed")
    # Act
    set_tx = token_farm.setPriceFeedContract(
        dapp_token.address, price_feed_address, {"from": account}
    )
    set_tx.wait(1)
    # Assert
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        set_tx2 = token_farm.setPriceFeedContract(
            dapp_token.address, price_feed_address, {"from": non_owner}
        )


def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    # Assert
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)
    # Act
    issue_tx = token_farm.issueTokens({"from": account})
    issue_tx.wait(1)
    assert dapp_token.balanceOf(account.address) == starting_balance + INITIAL_VALUE


def test_get_user_total_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    assert (
        token_farm.getUserTotalValue(account.address, {"from": account})
        == INITIAL_VALUE
    )
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    stake_tx = token_farm.stakeTokens(
        amount_staked, dapp_token.address, {"from": account}
    )
    stake_tx.wait(1)
    assert (
        token_farm.getUserTotalValue(account.address, {"from": account})
        == INITIAL_VALUE * 2
    )
    unstake_tx = token_farm.unstakeTokens(dapp_token.address, {"from": account})
    unstake_tx.wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getUserTotalValue(account.address, {"from": account})
