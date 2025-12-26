import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A 13-week journey from simulation to reality',
  favicon: 'img/favicon.ico',

  // Production URL (Vercel)
  url: 'https://book-navy-seven.vercel.app',
  baseUrl: '/',

  // GitHub Pages deployment config
  organizationName: 'your-username',
  projectName: 'physical-ai-book',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // SEO and performance meta tags
  headTags: [
    {
      tagName: 'meta',
      attributes: {
        name: 'description',
        content: 'Learn Physical AI and Humanoid Robotics through a 13-week hands-on course covering ROS 2, Gazebo, NVIDIA Isaac, and Voice-to-Action systems.',
      },
    },
    {
      tagName: 'meta',
      attributes: {
        name: 'keywords',
        content: 'physical AI, humanoid robotics, ROS 2, Gazebo, NVIDIA Isaac, simulation, robotics course',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'preconnect',
        href: 'https://fonts.googleapis.com',
      },
    },
  ],

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/Kelashkumar12345/physical-and-robotics-book/tree/001-physical-ai-book/book/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card.jpg',
    metadata: [
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'og:type', content: 'website' },
      { name: 'theme-color', content: '#2563eb' },
    ],
    navbar: {
      title: 'Physical AI Book',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      // Title links to docs intro
      hideOnScroll: false,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'courseSidebar',
          position: 'left',
          label: 'Course',
        },
        {
          href: 'https://github.com/Kelashkumar12345/physical-and-robotics-book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Course',
          items: [
            { label: 'Introduction', to: '/docs/intro' },
            { label: 'Module 1: ROS 2', to: '/docs/module-1-ros2/week-1-intro' },
            { label: 'Module 2: Gazebo', to: '/docs/module-2-gazebo/week-6-setup' },
            { label: 'Module 3: Isaac', to: '/docs/module-3-isaac/week-8-isaac-sdk' },
            { label: 'Module 4: VLA', to: '/docs/module-4-vla/week-11-humanoid' },
          ],
        },
        {
          title: 'Resources',
          items: [
            { label: 'Hardware Requirements', to: '/docs/hardware/requirements' },
            { label: 'GitHub', href: 'https://github.com/your-username/physical-ai-book' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Book. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml', 'json', 'markup'],
    },
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
