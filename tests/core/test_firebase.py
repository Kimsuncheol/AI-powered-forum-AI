"""Unit tests for Firebase authentication module."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.firebase import verify_firebase_token


@pytest.mark.asyncio
async def test_verify_firebase_token_missing_credentials():
    """Test that missing credentials raises 401."""
    with pytest.raises(HTTPException) as excinfo:
        await verify_firebase_token(None)
    
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Authorization header missing"


@pytest.mark.asyncio
@patch("app.core.firebase.auth.verify_id_token")
@patch("app.core.firebase.initialize_firebase")
async def test_verify_firebase_token_success(mock_init, mock_verify):
    """Test successful token verification."""
    # Setup mocks
    mock_creds = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_creds.credentials = "valid-token"
    
    expected_user = {"uid": "user-123", "email": "test@example.com"}
    mock_verify.return_value = expected_user
    
    # Execute
    result = await verify_firebase_token(mock_creds)
    
    # Assert
    assert result == expected_user
    mock_verify.assert_called_once_with("valid-token")
    mock_init.assert_called_once()


@pytest.mark.asyncio
@patch("app.core.firebase.auth.verify_id_token")
@patch("app.core.firebase.initialize_firebase")
async def test_verify_firebase_token_invalid(mock_init, mock_verify):
    """Test failed token verification raises 401."""
    # Setup mocks
    mock_creds = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_creds.credentials = "invalid-token"
    
    mock_verify.side_effect = Exception("Invalid token")
    
    # Execute & Assert
    with pytest.raises(HTTPException) as excinfo:
        await verify_firebase_token(mock_creds)
    
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid or expired token"
