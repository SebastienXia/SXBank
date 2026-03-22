import pytest
from unittest.mock import patch
from bank import Bank


# ================================
#           FIXTURE
# ================================

@pytest.fixture
def account():
    with patch("builtins.input", side_effect=["Sebastien", "Password1."]):
        return Bank()


# ================================
#           DEPOSIT
# ================================

def test_deposit_normal(account):
    account.balance = 0.0
    with patch("builtins.input", side_effect=["100.0", "test"]):
        account.deposit()
    assert account.balance == 100.0

def test_deposit_multiple(account):
    account.balance = 0.0
    with patch("builtins.input", side_effect=["100.0", "first", "50.0", "second"]):
        account.deposit()
        account.deposit()
    assert account.balance == 150.0


# ================================
#           WITHDRAWN
# ================================

def test_withdrawn_normal(account):
    account.balance = 100.0
    with patch("builtins.input", side_effect=["50.0", "test"]):
        account.withdrawn()
    assert account.balance == 50.0

def test_withdrawn_insufficient_funds(account):
    account.balance = 30.0
    # Solde insuffisant → relance input → on retire 20 cette fois
    with patch("builtins.input", side_effect=["50.0", "20.0", "test"]):
        account.withdrawn()
    assert account.balance == 10.0

def test_withdrawn_exact_balance(account):
    account.balance = 100.0
    with patch("builtins.input", side_effect=["100.0", "test"]):
        account.withdrawn()
    assert account.balance == 0.0


# ================================
#           SAVING
# ================================

def test_add_saving_normal(account):
    account.balance = 100.0
    with patch("builtins.input", side_effect=["test"]):
        account.add_saving(50.0)
    assert account.saving == 50.0
    assert account.balance == 50.0  # Balance débitée

def test_add_saving_insufficient_funds(account):
    account.balance = 10.0
    account.add_saving(50.0)        # Pas d'input car refusé avant
    assert account.saving == 0.0    # Saving inchangé
    assert account.balance == 10.0  # Balance inchangée

def test_add_saving_negative(account):
    account.balance = 100.0
    account.add_saving(-10.0)
    assert account.saving == 0.0

def test_remove_saving_normal(account):
    account.balance = 100.0
    account.saving = 50.0
    with patch("builtins.input", side_effect=["test"]):
        account.remove_saving(30.0)
    assert account.saving == 20.0
    assert account.balance == 130.0  # Balance créditée

def test_remove_saving_insufficient_funds(account):
    account.saving = 20.0
    account.remove_saving(50.0)     # Pas d'input car refusé avant
    assert account.saving == 20.0   # Saving inchangé

def test_remove_saving_negative(account):
    account.saving = 50.0
    account.remove_saving(-10.0)
    assert account.saving == 50.0


# ================================
#           CONNECT / DISCONNECT
# ================================

def test_disconnect(account):
    account.disconnect()
    assert account.connected == False

def test_connect_correct(account):
    account.disconnect()
    with patch("builtins.input", side_effect=["Sebastien", "Password1."]):
        account.connect()
    assert account.connected == True

def test_connect_wrong_password(account):
    account.disconnect()
    with patch("builtins.input", side_effect=["Sebastien", "WrongPass1.", "N"]):
        account.connect()
    assert account.connected == False

def test_connect_wrong_name(account):
    account.disconnect()
    with patch("builtins.input", side_effect=["WrongName", "N"]):
        account.connect()
    assert account.connected == False


# ================================
#           NAME / PASSWORD
# ================================

def test_name_valid(account):
    assert account.name == "Sebastien"

def test_name_too_short(account):
    # "A" est invalide → redemande → "Paul" est valide
    with patch("builtins.input", side_effect=["Paul"]):
        account.name = "A"
    assert account.name == "Paul"

def test_change_name(account):
    with patch("builtins.input", side_effect=["Password1.", "Pierre"]):
        account.change_name()
    assert account.name == "Pierre"

def test_change_name_wrong_password(account):
    with patch("builtins.input", side_effect=["WrongPass1.", "Q"]):
        account.change_name()
    assert account.name == "Sebastien"  # Inchangé

def test_change_password(account):
    import bcrypt
    with patch("builtins.input", side_effect=["Password1.", "NewPass1."]):
        account.change_password()
    assert bcrypt.checkpw("NewPass1.".encode('utf-8'), account._password)

def test_change_password_same(account):
    import bcrypt
    with patch("builtins.input", side_effect=["Password1.", "Password1.", "Password1.", "NewPass1."]):
        account.change_password()
    assert bcrypt.checkpw("NewPass1.".encode('utf-8'), account._password)


# ================================
#           SIMULATOR
# ================================

def test_simulator_rate(account):
    account.saving = 100.0
    # Vérifie que 1 an à 1.5% donne bien 101.5
    account.simulator_rate(1)
    expected = 100.0 + 100.0 * 1.5 / 100
    assert round(expected, 2) == 101.5