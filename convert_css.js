
// convert_css.js
const { convert } = require('css-to-tailwindcss');
const fs = require('fs');

const css = fs.readFileSync(0, 'utf-8');
try {
    const result = convert(css);
    console.log(result);
} catch (error) {
    console.error('Error converting CSS:', error);
    // console.log(''); // Output empty string on error
}
