// scripts/init-shardA-rs.js
rs.initiate(
   {
      _id: "shardA-rs",
      members: [
         { _id: 0, host: "shA1:27017" },
         { _id: 1, host: "shA2:27017" }
      ]
   }
)