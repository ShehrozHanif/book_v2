/**
 * Docusaurus Plugin to inject ChatBot component globally
 * This ensures the chatbot widget appears on every page
 */

const path = require('path');

module.exports = function (context, options) {
  return {
    name: 'chatbot-plugin',

    // Provide custom theme path
    getThemePath() {
      return path.resolve(__dirname, '../src/theme');
    },

    injectHtmlTags() {
      return {
        postBodyTags: [
          {
            tagName: 'div',
            attributes: {
              id: 'chatbot-root',
              style: 'position: fixed; z-index: 9999;'
            },
          },
          {
            tagName: 'script',
            innerHTML: `
(function() {
  // Inject chatbot after React hydration
  window.addEventListener('load', function() {
    const chatbotRoot = document.getElementById('chatbot-root');
    if (chatbotRoot && window.__DOCUSAURUS_CHATBOT__) {
      window.__DOCUSAURUS_CHATBOT__.mount(chatbotRoot);
    }
  });
})();
            `,
          },
        ],
      };
    },
  };
};
