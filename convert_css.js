
// convert_css.js
const { convert } = require('css-to-tailwindcss');
const fs = require('fs');

// 读取输入的CSS内容
const css = fs.readFileSync(0, 'utf-8');

try {
    // 转换CSS为Tailwind类
    const result = convert(css);
    
    // 检查结果是否有效
    if (result && typeof result === 'object' && result.tailwindClasses) {
        // 输出Tailwind类名（以空格分隔的字符串）
        console.log(result.tailwindClasses.join(' '));
    } else if (typeof result === 'string') {
        // 如果结果是字符串，直接输出
        console.log(result);
    } else {
        // 如果转换没有返回有效结果，输出空字符串而不是错误
        console.log('');
    }
} catch (error) {
    // 发生错误时输出空字符串而不是错误信息
    console.error('Error converting CSS:', error);
    console.log('');
}
