#!/bin/bash
# 🤖 Ollama Kurulum Scripti
# ========================

echo "🤖 Ollama kurulumu başlıyor..."

# Ollama'yı indir ve kur
curl -fsSL https://ollama.ai/install.sh | sh

echo "📦 Model indiriliyor..."

# Küçük, hızlı model indir
ollama pull llama3.2:3b

echo "✅ Kurulum tamamlandı!"
echo ""
echo "🚀 Kullanım:"
echo "  ollama run llama3.2:3b"
echo ""
echo "🔧 Servis olarak başlat:"
echo "  ollama serve"
echo ""
echo "📊 Model listesi:"
echo "  ollama list"
