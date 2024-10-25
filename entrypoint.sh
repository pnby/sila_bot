#!/usr/bin/sh

ollama serve &

sleep 5

ollama run qwen2:7b-instruct-fp16

wait