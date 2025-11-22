// scripts/init-shardB-rs.js
rs.initiate(
   {
      _id: "shardB-rs",
      members: [
         { _id: 0, host: "shB1:27017" },
         { _id: 1, host: "shB2:27017" }
      ]
   }
)