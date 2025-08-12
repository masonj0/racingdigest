#!/bin/bash

# Racing Scanner Icon Generator
# This script creates placeholder icons for the PWA

echo "🎯 Creating placeholder icons for Racing Scanner PWA..."

# Create a simple SVG icon
cat > icon.svg << 'EOF'
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#007bff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0056b3;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="64" fill="url(#grad)"/>
  <text x="256" y="200" font-family="Arial, sans-serif" font-size="120" font-weight="bold" text-anchor="middle" fill="white">🎯</text>
  <text x="256" y="320" font-family="Arial, sans-serif" font-size="48" font-weight="bold" text-anchor="middle" fill="white">RACING</text>
  <text x="256" y="380" font-family="Arial, sans-serif" font-size="32" font-weight="bold" text-anchor="middle" fill="white">SCANNER</text>
</svg>
EOF

# Check if ImageMagick is available
if command -v convert >/dev/null 2>&1; then
    echo "📱 Converting SVG to PNG icons..."
    
    # Convert to different sizes
    convert icon.svg -resize 192x192 icon-192.png
    convert icon.svg -resize 512x512 icon-512.png
    convert icon.svg -resize 152x152 icon-152.png
    convert icon.svg -resize 180x180 icon-180.png
    
    echo "✅ Icons created successfully!"
    echo "📁 Generated files:"
    ls -la icon-*.png
    
    # Clean up SVG
    rm icon.svg
    
else
    echo "⚠️  ImageMagick not found. Creating placeholder files..."
    echo "📝 To generate proper icons, install ImageMagick:"
    echo "   pkg install imagemagick"
    echo "   or"
    echo "   apt install imagemagick"
    
    # Create placeholder files
    echo "Placeholder icon - replace with your own" > icon-192.png
    echo "Placeholder icon - replace with your own" > icon-512.png
    echo "Placeholder icon - replace with your own" > icon-152.png
    echo "Placeholder icon - replace with your own" > icon-180.png
    
    echo "📁 Placeholder files created:"
    ls -la icon-*.png
    echo ""
    echo "💡 Replace these files with your own icons for a better PWA experience!"
fi

echo ""
echo "🎯 PWA icons ready! The racing scanner can now be added to your home screen."