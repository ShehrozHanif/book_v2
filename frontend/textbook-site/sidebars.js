// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  tutorialSidebar: [
    'intro',
    'getting-started',
    {
      type: 'category',
      label: 'Module 1: Foundations',
      collapsed: true,
      items: [
        'module-01/index',
        'module-01/chapter-01',
        'module-01/chapter-02',
        'module-01/chapter-03',
        'module-01/chapter-04',
        'module-01/chapter-05',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: ROS2 & Development',
      collapsed: true,
      items: [
        'module-02/index',
        'module-02/chapter-06',
        'module-02/chapter-07',
        'module-02/chapter-08',
        'module-02/chapter-09',
        'module-02/chapter-10',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: Advanced Kinematics & Motion',
      collapsed: true,
      items: [
        'module-03/index',
        'module-03/chapter-11',
        'module-03/chapter-12',
        'module-03/chapter-13',
        'module-03/chapter-14',
        'module-03/chapter-15',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Learning & Control',
      collapsed: true,
      items: [
        'module-04/index',
        'module-04/chapter-16',
      ],
    },
    {
      type: 'category',
      label: 'Module 5: Applications & Future',
      collapsed: true,
      items: [
        'module-05/index',
        'module-05/chapter-17',
        'module-05/chapter-18',
        'module-05/chapter-19',
        'module-05/chapter-20',
        'module-05/chapter-21',
        'module-05/chapter-22',
      ],
    },
  ],
};

export default sidebars;
