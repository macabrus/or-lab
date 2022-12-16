#!/bin/env bash

API="http://localhost:8080/api"
MIME="Content-Type: application/json"

echo --- Test fetch all ---
curl -s "$API/plant?size=100" | jq '[.[] | {id,name}]'

echo --- Test fetch by id ---
curl -s "$API/plant/1"

echo --- Test add new plant ---
CREATE='{"name": "Another Aloe"}'
curl -s -H "$MIME" -d "$CREATE" "$API/plant"

# fetch id of created plant
FILTER=$(lab query encode '{"name": "Another"}')
PLANT_ID=$(curl -s "$API/plant?filter=$FILTER" | jq '.[] | .id')

echo --- Test update plant ---
UPDATE='{"is_edible": true}'
curl -s -X PATCH -H "$MIME" -d "$UPDATE" "$API/plant/$PLANT_ID"
curl -s "$API/plant/$PLANT_ID" # check if updated

echo --- Test delete plant ---
curl -s -X DELETE "$API/plant/$PLANT_ID"
