// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'A comprehensive guide to building and programming humanoid robots',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://ShehrozHanif.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/book_v2/',

  // GitHub pages deployment config.
  organizationName: 'ShehrozHanif',
  projectName: 'book_v2',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'warn',

  // Load Noto Nastaliq Urdu font for Urdu translation feature
  stylesheets: [
    'https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap',
  ],

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Robotics Textbook',
        logo: {
          alt: 'Robotics Textbook Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            to: '/docs/module-01/',
            position: 'left',
            label: 'Chapters',
          },
          {
            label: '🎓 Learning',
            position: 'right',
            items: [
              {
                label: '🚀 Get Started',
                to: '/onboarding',
              },
              {
                to: '/dashboard',
                label: '📊 Dashboard',
                className: 'navbar-dashboard-link',
              },
              {
                label: '🏆 My Achievements',
                to: '/achievements',
              },
              {
                label: '📈 Progress',
                to: '/progress',
              },
            ],
          },
          {
            href: 'https://github.com/ShehrozHanif/book_v2',
            label: 'GitHub',
            position: 'right',
          },
          {
            to: '/login',
            label: '🔐 Login',
            position: 'right',
            className: 'navbar-login-link',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Resources',
            items: [
              {
                label: 'Chapters',
                to: '/docs/module-01/chapter-01',
              },
              {
                label: 'About',
                to: '/',
              },
            ],
          },
          {
            title: 'External Links',
            items: [
              {
                label: 'GitHub Repository',
                href: 'https://github.com/ShehrozHanif/book_v2',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'yaml', 'markup'],
      },
    }),
};

export default config;
