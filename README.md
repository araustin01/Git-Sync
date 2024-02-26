# Git-Sync

The Git Sync project is designed to streamline development workflow, enabling easier collaboration among team members. Here's how it works:

### Objective

The primary goal of this project is to standardize development workflow, making it simpler for team members to collaborate effectively. By utilizing Git, we can ensure that the designated remote repository remains up-to-date with the latest changes automatically, facilitating easy cloning and pulling of the latest server versions for development purposes.

#### Figure

<center>
<img src="https://cdn.discordapp.com/attachments/855846074283589642/1190505714347679795/gitsync.drawio.png?ex=65ebdfd8&is=65d96ad8&hm=6c3fa81c9e2ee8f8a00a7da0df275821c9f25d5d80668d94bb29ab27ffe6e959&" width="400">
</center>

### How it Works

1. **Up-to-Date Server Repository:** The designated server's Git remote repository will always reflect the latest server files. This ensures that team members can clone or pull the latest versions of the server and make necessary changes with confidence.
<br>
2. **Automated Synchronization:** Subsequent pushes and merges with the main branch will automatically synchronize locally and update the server. This synchronization process is triggered by invoking the update.py program, which merges the staging layer with its source. This automation eliminates the need for tedious manual copying of changes to the server directory.
<br>
3. **Utilization of Git's Version Management:** By leveraging Git's version management capabilities, we can effectively track changes and collaborate seamlessly. Git serves as a powerful tool for managing code changes, facilitating collaboration, and ensuring version control.

### Local Development

The presence of a staging directory enables team members to make changes locally without disrupting the synchronization process. This setup ensures that local changes can be quickly implemented without affecting the overall workflow. 

### Conclusion

The Git Sync project offers a robust solution for managing our development workflow, promoting collaboration, and ensuring the stability of our system. By leveraging Git and automation, we can streamline processes and enhance productivity.