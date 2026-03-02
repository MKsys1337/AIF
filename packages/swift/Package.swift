// swift-tools-version: 5.9

// Adaptive Image Format (AIF) — Swift Package
// Copyright (C) 2026 Markus Köplin
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.

import PackageDescription

let package = Package(
    name: "AIF",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
    ],
    products: [
        .library(
            name: "AIF",
            targets: ["AIF"]
        ),
    ],
    targets: [
        .target(
            name: "AIF",
            path: "Sources/AIF"
        ),
        .testTarget(
            name: "AIFTests",
            dependencies: ["AIF"],
            path: "Tests/AIFTests"
        ),
    ]
)
