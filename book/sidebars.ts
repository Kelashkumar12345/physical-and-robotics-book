import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  courseSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Hardware Requirements',
      items: ['hardware/requirements'],
    },
    {
      type: 'category',
      label: 'Module 1: ROS 2 (Weeks 1-5)',
      collapsed: false,
      items: [
        'module-1-ros2/week-1-intro',
        'module-1-ros2/week-2-sensors',
        'module-1-ros2/week-3-nodes',
        'module-1-ros2/week-4-topics',
        'module-1-ros2/week-5-services',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Gazebo & Unity (Weeks 6-7)',
      items: [
        'module-2-gazebo/week-6-setup',
        'module-2-gazebo/week-7-urdf',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac (Weeks 8-10)',
      items: [
        'module-3-isaac/week-8-isaac-sdk',
        'module-3-isaac/week-9-perception',
        'module-3-isaac/week-10-nav2',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: VLA (Weeks 11-13)',
      items: [
        'module-4-vla/week-11-humanoid',
        'module-4-vla/week-12-locomotion',
        'module-4-vla/week-13-capstone',
      ],
    },
  ],
};

export default sidebars;
