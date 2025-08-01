// Configuration for GitHub Pages site
const config = {
    // Replace with your actual GitHub username
    githubUsername: 'Folis455',
    
    // Repository name
    repoName: 'TikTok-to-Shorts-Reels-Reuploader',
    
    // Site settings
    siteTitle: 'TikTok to Shorts/Reels Uploader 2025',
    siteDescription: 'Automatically repost your TikToks to YouTube Shorts and Instagram Reels while maintaining original quality, without watermarks and with the new extended durations.',
    
    // Social links
    socialLinks: {
        github: 'https://github.com/Folis455/TikTok-to-Shorts-Reels-Reuploader',
        issues: 'https://github.com/Folis455/TikTok-to-Shorts-Reels-Reuploader/issues',
        license: 'https://github.com/Folis455/TikTok-to-Shorts-Reels-Reuploader/blob/main/LICENSE'

    }
};

// Function to update all GitHub links with the correct username
function updateGitHubLinks() {
    const username = config.githubUsername;
    const repoName = config.repoName;
    
    // Update all GitHub links
    const githubLinks = document.querySelectorAll('a[href*="YOUR_USERNAME"]');
    githubLinks.forEach(link => {
        link.href = link.href.replace('YOUR_USERNAME', username);
    });
    
    // Update download link
    const downloadLink = document.querySelector('a[href*="archive/refs/heads/main.zip"]');
    if (downloadLink) {
        downloadLink.href = `https://github.com/${username}/${repoName}/archive/refs/heads/main.zip`;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    updateGitHubLinks();
}); 